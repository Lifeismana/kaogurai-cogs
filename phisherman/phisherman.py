import re
from urllib.parse import urlparse

import aiohttp
import discord
from redbot.core import Config, commands


class PhisherMan(commands.Cog):
    """
    Protects users against phishing attacks.
    """

    __version__ = "1.0.0"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=73835)
        self.config.register_guild(
            enabled=False, safe="ignore", suspicious="delete", malicious="ban"
        )
        self.session = aiohttp.ClientSession()
        self.bot.loop.create_task(self.set_token())

    def cog_unload(self):
        self.bot.loop.create_task(self.session.close())

    async def red_delete_data_for_user(self, **kwargs):
        return

    def format_help_for_context(self, ctx):
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}"

    async def set_token(self):
        token = await self.bot.get_shared_api_tokens("phisherman")
        self.key = token.get("key")

    @commands.Cog.listener()
    async def on_red_api_tokens_update(self, service_name, api_tokens):
        if service_name == "phisherman":
            self.key = api_tokens.get("key")

    def extract_urls(self, message: str):
        """
        Extract URLs from a message.

        RegEx Source: https://regex101.com/r/03VgN5/5/
        """
        return re.findall(
            r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b",
            message,
        )

    def get_domains_from_urls(self, urls: list):
        """
        Extracts the domains from the urls.
        """
        domains = []
        for url in urls:
            parsed = urlparse(url)
            domains.append(parsed.netloc)

    async def get_domain_info(self, url: str):
        """
        Get information about a domain.
        """

    async def get_domain_safety(self, url: str):
        """
        Get safety information about a domain.

        Possible outcomes are: "safe", "suspicious", "malicious"
        """

    @commands.Cog.listener()
    async def on_message_without_command(self, message: discord.Message):
        """
        Handles the logic for checking URLs.
        """
        if not message.guild or not message.author.bot:
            return
        if await self.bot.cog_disabled_in_guild(self, message.guild):
            return
        if not await self.config.guild(message.guild).enabled():
            return

        urls = self.extract_urls(message.content)
        if not urls:
            return

        domains = self.get_domains_from_urls(urls)
        for domain in domains:
            ...

    @commands.command(aliases=["checkforphish", "checkscam", "checkforscam"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def checkphish(self, ctx, url: str):
        """
        Check if a url is a phishing scam.
        """

    @commands.group()
    @commands.guild_only()
    @commands.is_admin_or_permissions(manage_guild=True)
    async def phisherman(self, ctx):
        """
        Settings to set the phisherman integration.
        """
