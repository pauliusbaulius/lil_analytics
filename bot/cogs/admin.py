import os
import time

import discord
from discord.ext import commands



class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(kick_members=True)
    @commands.command()
    async def kick(self, ctx, member: discord.Member, *, reason="My dad used to kick my ass too :,)"):
        """Kicks mentioned user(s) from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"lil_analytics@matrix: {member} > /dev/null")

    @commands.has_permissions(ban_members=True)
    @commands.command()
    async def ban(self, ctx, member: discord.Member, *, reason="You wake up from the simulation..."):
        """Bans mentioned user(s) from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"lil_analytics@matrix: {member} > /dev/null")

    @commands.has_permissions(manage_messages=True)
    @commands.command()
    async def clear(self, ctx, amount):
        """Deletes given amount of messages from the channel. Keyword 'all' deletes all messages."""
        try:
            if int(amount) > 0:
                await ctx.channel.purge(limit=int(amount) + 1)  # +1 to delete the .clear message too.
                await ctx.send(f'Permanently removed {amount} message(s) in this channel.')

        except ValueError:
            if amount == "all":
                await ctx.channel.purge(limit=None)
                await ctx.channel.send(f"Press F for this channel. All messages have been nuked.")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def gdpr(self, ctx, member: discord.Member):
        bef = time.time()
        await ctx.send(f"Going to delete all messages by {member}.")
        counter = 0
        async for message in ctx.channel.history(limit=None):
            if message.author == member:
                counter += 1
                await message.delete(delay=None)
        aft = time.time()
        await ctx.send(f"Deleted {counter} message(s) by {member} in "
                       f"{time.strftime('%H:%M:%S', time.gmtime(int(aft - bef)))}.")

    # @commands.has_permissions(administrator=True)
    # @commands.command()
    # async def export(self, ctx, mention: discord.Member, *, limit: int = None):
    #     """Magnum Opus of functions doing a ton of work. Exports mentioned users chat history as csv file.
    #
    #     Can be given a limit as a guideline. If there is no limit given, it will export all messages!
    #     Exporting all messages might take a really long time.
    #
    #     This function iterates all channels of the guild and iterates all messages in history.
    #     Messages written by mentioned user are then extracted and written to a csv file.
    #     File is uploaded after whole history is iterated. This function is probably the reason this bot will be banned.
    #     File is deleted after upload.
    #     """
    #     bef = time.time()
    #     counter = 0
    #     filename = os.path.join(definitions.temporary_dir, f"messages_{mention}.csv")
    #     messages = ["CREATED_UTC;CHANNEL_NAME;CONTENT;ATTACHMENTS\n"]
    #
    #     # Delete previous file in case there is one.
    #     if os.path.isfile(filename):
    #         await ctx.send("File is already being generated, be patient...")
    #         return
    #
    #     await ctx.send(f"Going to export {'all' if limit is None else limit} messages by {mention}. "
    #                    f"This can take from a few minutes up to a whole day. "
    #                    f"Bot has to iterate complete history if you want all messages!")
    #
    #     for channel in ctx.guild.text_channels:
    #         async for message in channel.history(limit=limit):
    #             if counter == limit:
    #                 break
    #
    #             if message.author == mention:
    #                 messages.append(f"{message.created_at};"
    #                                 f"{message.channel.name};"
    #                                 f"{message.clean_content};"
    #                                 f"{[a.url for a in message.attachments]}\n")
    #                 counter += 1
    #             # Write to file each 100 messages in memory.
    #             if counter % 100 == 0:
    #                 with open(filename, "a") as f:
    #                     f.writelines(messages)
    #                 messages.clear()
    #
    #     # If there are messages remaining, write them to the file.
    #     if messages:
    #         with open(filename, "a") as f:
    #             f.writelines(messages)
    #
    #     aft = time.time()
    #
    #     # TODO open and sort before sending, sort by time!
    #
    #     with open(filename, 'rb') as fp:
    #         await ctx.send(f"Exported {counter} message(s) by {mention} in "
    #                        f"{time.strftime('%H:%M:%S', time.gmtime(int(aft - bef)))}. "
    #                        f"This is all I could find given {'all' if limit is None else limit} as the limit. ",
    #                        file=discord.File(fp, f"messages_{mention}.csv"))
    #
    #     # Delete after uploading it.
    #     os.remove(filename)


def setup(client):
    client.add_cog(Admin(client))
