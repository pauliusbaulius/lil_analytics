import os

from discord.ext import commands

from bot.root import ROOT_DIR
from bot.utils import is_owner


class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def cogs(self, ctx):
        """Lists all .py files in cogs/ directory."""
        cogs = [filename[:-3] for filename in os.listdir(os.path.join(ROOT_DIR, "cogs")) if filename.endswith(".py")]
        await ctx.send(f"`available cogs: {', '.join(cogs)}`")


def setup(client):
    client.add_cog(Owner(client))
