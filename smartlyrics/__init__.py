from redbot.core.bot import Red
from .smartlyrics import SmartLyrics


async def setup(bot: Red) -> None:
    cog = SmartLyrics(bot)
    bot.add_cog(cog)


__red_end_user_data_statement__ = "This cog does not store any end user data."
