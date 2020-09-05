import asyncio

import discord
from discord.ext import commands
import random

class Personal(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def silence(self, ctx):
        laminatas = ctx.message.guild.get_member(257945590799925249)
        timeout = random.randint(30, 240)
        role = discord.utils.get(ctx.guild.roles, name="silence")
        if not role:
            try:
                role = await ctx.guild.create_role(name="silence", reason="Tvarka ir teisingumas. Laminatas tylus.")
                for channel in ctx.guild.channels:
                    await channel.set_permissions(role, send_messages=False)
            except discord.Forbidden:
                return await ctx.send("I have no permissions to make a muted role.")
        if not "silence" in [role.name for role in laminatas.roles]:
            await laminatas.add_roles(role)
            await ctx.send(f"Laminatas patylės lygiai {timeout} sekundes.")
            await asyncio.sleep(timeout)
            await laminatas.remove_roles(discord.utils.get(ctx.guild.roles, name="silence"))
        else:
            await ctx.send("Laminatas jau tyli...")




def setup(client):
    client.add_cog(Personal(client))
