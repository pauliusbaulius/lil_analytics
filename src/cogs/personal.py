import asyncio

import discord
from discord.ext import commands
import random

class Personal(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["laminat", "patylek", "stfu"])
    async def silence(self, ctx):
        laminatas = ctx.message.server.get_member(257945590799925249)
        timeout = random.randint(30, 240)
        role = discord.utils.get(ctx.guild.roles, name="silence")
        if not role:
            muted = await ctx.guild.create_role(name="silence", reason="Tvarka ir teisingumas. Laminatas tylus.")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted, send_messages=False, read_message_history=False, read_messages=False)

        await laminatas.add_roles(muted)
        await ctx.send(f"Laminatas patylės lygiai {timeout} sekundes.")

        await asyncio.sleep(timeout)
        await laminatas.remove_roles(discord.utils.get(ctx.guild.roles, name="silence"))


def setup(client):
    client.add_cog(Personal(client))
