from discord.ext import commands

"""
    
"""


class Template(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def foo(self):
        pass


def setup(client):
    client.add_cog(Template(client))
