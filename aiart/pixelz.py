import argparse
import asyncio
import random
import string
from io import BytesIO

import discord
from PIL import Image
from redbot.core import commands
from redbot.core.commands import BadArgument, Context, Converter

from .abc import MixinMeta

PIXELZ_FILTERS = ["Oil Painting", "Watercolour", "Cosmic", "Fantasy", "Cyberpunk", "Cubist"]
PIXELZ_ARTISTS = ["Van Gogh", "Salvador Dali", "Pablo Picasso", "Banksy", "Henri Matisse", "Michelangelo", "Andy Warhol", "Rembrandt", "Vermeer", "Jean-Antoine Watteau", "Eugene Delacroix", "Claude Monet", "Georges Seurat", "Edvard Munch", "Egon Schiele", "Gustav Klimt", "Rene Magritte", "Georgia O'Keeffe", "Edward Hopper", "Frida Kahlo", "Jackson Pollock", "Yayoi Kusama"]

# A lot of the code for parsing the arguments is taken from flare's giveaways cog
# https://github.com/flaree/flare-cogs/blob/master/giveaways/converter.py


class NoExitParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise BadArgument()


class PixelzArguments(Converter):

    def get_parser(self) -> NoExitParser:
        parser = NoExitParser(add_help=False)
        parser.add_argument("prompt", type=str, nargs="*")
        parser.add_argument(
            "--algorithm", type=str, default="artistic", nargs="?"
        )
        parser.add_argument(
            "--aspect",
            "--aspect-ratio",
            type=str,
            default="square",
            nargs="?",
        )
        parser.add_argument("--filter", type=str, default=None, nargs="*")
        parser.add_argument("--artist", type=str, default=None, nargs="*")
        parser.add_argument(
            "--symmetric", type=bool, default=False, nargs="?"
        )
        return parser


    async def convert(self, ctx: Context, argument: str) -> str:
        argument = argument.replace("—", "--")  # For iOS's weird smart punctuation

        parser = self.get_parser()

        try:
            values = vars(parser.parse_args(argument.split(" ")))
        except Exception:
            raise BadArgument(
                self.get_help_text()
            )

        if not values["prompt"]:
            raise BadArgument(
                self.get_help_text()
            )

        values["prompt"] = " ".join(values["prompt"])

        if len(values["prompt"]) > 239:
            raise BadArgument(
                "Prompt is too long. Please keep it under 240 characters."
            )

        if values["artist"]:
            values["artist"] = " ".join(values["artist"])

        if values["filter"]:
            values["filter"] = " ".join(values["filter"])

        return values
        


class PixelzCommand(MixinMeta):
    """
    Implements the Internal Pixelz API used in their web client.
    """

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def pixelz(self, ctx: Context, *, arguments: PixelzArguments):
        """
        Generate art using Pixelz.
        """


        async with ctx.typing():

            user_id = "".join(
                random.choice(string.ascii_letters + string.digits) for _ in range(28)
            )

            data = {
                "prompts": [
                    {
                        "prompt": arguments["prompt"],
                        "weight": 1,
                        "public": True,
                    }
                ],
                "public": True,
                "style": "guided",
                "quality": "normal",
                "user_id": user_id,
            }

            async with self.session.post(
                "https://api.pixelz.ai/preview", json=data
            ) as req:
                if req.status != 200:
                    await ctx.send("Failed to generate art. Please try again later.")
                    return
                json = await req.json()

            if json["success"] is False:
                await ctx.send("Failed to generate art. Please try again later.")
                return

            image_id = json["process"]["generated_image_id"]

            for x in range(60):
                if x == 99:
                    await ctx.send("Failed to generate art. Please try again later.")
                    return

                headers = {
                    "Referer": "https://pixelz.ai/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
                }
                async with self.session.get(
                    f"https://storage.googleapis.com/pixelz-images/{user_id}/{image_id}/output_c.jpg",
                    headers=headers,
                ) as req:
                    if req.status == 200:
                        break
                await asyncio.sleep(10)

            async def get_image(index: int):
                headers = {
                    "Referer": "https://pixelz.ai/",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
                }
                async with self.session.get(
                    f"https://storage.googleapis.com/pixelz-images/{user_id}/{image_id}/{index}.png",
                    headers=headers,
                ) as req:
                    return await req.read()

            images = [get_image(i) for i in range(6)]
            resps = await asyncio.gather(*images)

            image_list = [Image.open(BytesIO(image)) for image in resps]

            width = max(image.width for image in image_list)
            height = max(image.height for image in image_list)

            new_image = Image.new("RGB", (width * 3, height * 2))

            for i in range(2):
                for j in range(3):
                    new_image.paste(image_list[i * 2 + j], (width * j, height * i))

            buffer = BytesIO()
            new_image.save(buffer, format="PNG")
            buffer.seek(0)

            embed = discord.Embed(
                title="Here's your art!",
                description="Type the number next to the image to select it. If you want more than one image, seperate the numbers with a comma.",
                color=await ctx.embed_color(),
            )
            embed.set_image(url="attachment://craiyon.png")
            await ctx.send(embed=embed, file=discord.File(buffer, "craiyon.png"))

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                msg = await self.bot.wait_for("message", check=check, timeout=30)
            except asyncio.TimeoutError:
                return

            try:
                selected = [int(i) for i in msg.content.split(",")]
                selected = [image_list[i - 1] for i in selected]
            except:
                return

            for image in selected:
                buffer = BytesIO()
                image.save(buffer, format="PNG")
                buffer.seek(0)
                await ctx.send(file=discord.File(buffer, "pixelz.png"))
