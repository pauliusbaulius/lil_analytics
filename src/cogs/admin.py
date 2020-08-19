import logging
import time

import discord
from discord.ext import commands


"""
    General functions for administrators, like kicking, banning, muting users.
    Also functions related to the bot functionality: 
        1. clear - deletes messages in a channel, can nuke whole channel pretty fast.
        2. gdpr - deletes all messages sent by the caller of the function.
"""


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="You did not make it."):
        """Kicks mentioned user(s) from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"{member} > /dev/null")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="Booted back into the simulation."):
        """Bans mentioned user(s) from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"{member} > /dev/null")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def mute(self, user, time):
        """Mutes mentioned user(s) for given amount of time. Amount should be integer."""
        # TODO https://www.youtube.com/watch?v=GRPOFOztFR4&list=WL&index=30&t=0s
        pass

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def clear(self, ctx, amount):
        """Deletes given amount of messages from the channel. Keyword 'all' deletes all messages."""
        try:
            if int(amount) > 0:
                await ctx.channel.purge(limit=int(amount) + 1)  # +1 to delete the .clear message too.
                await ctx.send(f'Permanently removed {amount} message(s) in this channel.', delete_after=10)

        except ValueError:
            if amount == "all":
                await ctx.channel.purge(limit=None)
                await ctx.channel.send(f"Press F for this channel. All messages have been nuked.")

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def gdpr(self, ctx):
        # TODO should take users as arguments and delete their messages!
        bef = time.time()
        await ctx.send(f"Going to delete all messages by {ctx.message.author}", delete_after=10)
        counter = 0
        async for message in ctx.channel.history(limit=None):
            if message.author == ctx.message.author:
                counter += 1
                await message.delete(delay=None)
        aft = time.time()
        await ctx.send(f"Deleted {counter} message(s) by {ctx.message.author} in {aft - bef:.2f} s.")


def setup(client):
    client.add_cog(Admin(client))
