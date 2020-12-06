import os

from discord.ext import commands

from bot.definitions import root_dir

"""
    Some additional functions for me or you - if you are running this.
"""


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def cogs(self, ctx):
        """Lists all .py files in cogs/ directory."""
        cogs = [
            filename[:-3]
            for filename in os.listdir("cogs")
            if filename.endswith(".py")
        ]
        await ctx.send(f"Available cogs: {', '.join(cogs)}")


def setup(client):
    client.add_cog(Owner(client))
