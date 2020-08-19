import os

from discord.ext import commands

from definitions import root_dir
from src.dml import add_reply
from src.utils import is_owner


"""
    Some additional functions for me or you - if you are running this.
"""


class Owner(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def add_reply(self, ctx, *text: str):
        """Adds a new reply to the database for bot to use. Replies are responses bot uses when tagged or when any
        message contains word 'bot'.
        """
        if is_owner(ctx.message.author.id):
            add_reply(" ".join(text))
            await ctx.send("Added new reply to the database!")

    @commands.command()
    async def cogs(self, ctx):
        """Lists all .py files in cogs/ directory."""
        cogs = [
            filename[:-3]
            for filename in os.listdir(os.path.join(root_dir, "src/cogs"))
            if filename.endswith(".py")
        ]
        await ctx.send(f"Available cogs: {', '.join(cogs)}")


def setup(client):
    client.add_cog(Owner(client))
