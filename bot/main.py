import datetime
import os
import sys
from typing import List

import discord
from discord.ext import commands

from bot import definitions, api, sqlite, dml as db, ddl
from bot.decorators import timer
from bot.root import ROOT_DIR
from bot.utils import find_word, is_owner, is_me

client = commands.Bot(command_prefix=commands.when_mentioned_or(definitions.command_prefix))
client.remove_command("help")


def start_bot():
    print("lil analytics: Calling start_bot() in main.py!")

    # print("lil analytics: Adding src/ to syspath!")
    # sys.path.insert(0, definitions.root_dir)

    print("lil analytics: Building database schema if database is empty.")
    ddl.build_database()

    print("lil analytics: Loading cogs.")
    # Load all cogs by default.
    for filename in os.listdir(os.path.join(ROOT_DIR, "cogs")):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    print("lil analytics: Connecting to Discord and starting the client...")
    client.run(definitions.bot_token)


@client.event
async def on_ready():
    """This runs if everything goes right. Starts background processes."""
    await client.change_presence(activity=discord.Game(name=definitions.status_message))
    print("lil analytics: Bot is now running!")

    print("lil analytics: Background indexing of messages in last 24h started!")
    time_before = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    for guild_id in [g.id for g in client.guilds]:
        await client.loop.create_task(db.background_parse_history(client=client, guild_id=guild_id, after=time_before))


@timer
@client.command()
async def load(ctx, extension):
    """Loads cog from cogs folder."""
    if is_owner(ctx.message.author.id):
        try:
            client.load_extension(f"cogs.{extension}")
            await ctx.send(f"Loaded extension [{extension}]")
        except ModuleNotFoundError:
            await ctx.send(f"Extension [{extension}] does not exist.")
    else:
        await ctx.send(f"You can't do this.")


@timer
@client.command()
async def unload(ctx, extension):
    """Unloads cog from cogs folder."""
    if is_owner(ctx.message.author.id):
        try:
            client.unload_extension(f"cogs.{extension}")
            await ctx.send(f"Unloaded extension [{extension}]")
        except ModuleNotFoundError:
            await ctx.send(f"Extension [{extension}] does not exist.")
    else:
        await ctx.send(f"You can't do this.")


@client.command()
async def shutdown(ctx):
    """Stops bot and closes db connection. Can be executed by the owner only."""
    if is_owner(ctx.message.author.id):
        await ctx.send("`lil_analytics@matrix:~$ shutdown -h 'lol rip'`")
        print("lil analytics: Shutting down...")
        sqlite.close_connection()
        await client.logout()


@client.event
async def on_message(message):
    """This is where you can add functions that react to user messages that
    are not direct commands. """

    # Prevent recursive calls.
    if message.author == client.user:
        await db.add_message(message)
        return

    # Check if message contains word "bot" or mentions this bot. Reply with a message if true.
    if find_word(message.content.lower(), "lil analytics") or is_me(message.mentions):
        reply = db.get_reply()
        await message.channel.send(reply)

    # Add message metadata to database.
    await db.add_message(message)
    await api.add_message(message)

    # Handle other commands.
    await client.process_commands(message)



# TODO

@client.event
async def on_bulk_message_delete(messages: List[discord.Message]):
    print("on_bulk_message_delete", messages)
    await db.message_bulk_delete(messages)

    for message in messages:
        await api.delete_message(message.id)


@client.event
async def on_raw_bulk_message_delete(payload: discord.RawBulkMessageDeleteEvent):
    """Discord gives minimal amount of data, this will create holes in
    database if the server was not parsed with .parse_history first!"""
    print("on_raw_bulk_message_delete", payload)
    await db.message_bulk_delete(payload.message_ids)

    for message_id in payload.message_ids:
        await api.delete_message(message_id)



@client.event
async def on_message_delete(message: discord.Message):
    """Updates database metadata for message. Sets flag that message is gone and when it was deleted."""
    print("on_message_delete", message)
    await db.message_delete(message.id)

    await api.delete_message(message.id)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    """Discord gives minimal amount of data, this will create holes in
    database if the server was not parsed with .parse_history first!"""
    print("on_raw_message_delete", payload)
    await db.message_delete(payload.message_id)

    await api.delete_message(payload.message_id)


@client.event
async def on_message_edit(before, after):
    """Updates database metadata for message."""
    await db.message_update(message=after)

    await api.add_message(after)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    await db.message_update(message_raw=payload)

    await api.add_message(payload)


# TODO handle and send to add_reaction!

@client.event
async def on_reaction_add(reaction, user):
    """Updates database metadata for user reactions."""
    await db.add_reaction(reaction, user.id)

    await api.add_reaction(reaction)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Updates database metadata for user reactions."""
    await db.add_reaction_raw(payload.message_id, payload.emoji, payload.user_id)

    await api.add_reaction(payload)


@client.event
async def on_reaction_remove(reaction, user):
    """Updates database metadata for user reactions."""
    await db.remove_reaction(reaction, user.id)

    await api.delete_reaction(message_id=reaction.message.id, reaction_id=reaction.message.author.id, reacted_id=user.id)


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Updates database metadata for user reactions."""
    await db.remove_reaction_raw(payload.message_id, payload.emoji, payload.user_id)

    await api.delete_reaction(payload.message_id, payload.emoji, payload.user_id)


@client.event
async def on_reaction_clear(message, reactions):
    # TODO remove all reactions for message.id
    print("on_reaction_clear", message)


@client.event
async def on_raw_reaction_clear(payload):
    # TODO remove all reactions for message.id
    print("on_raw_reaction_clear ", payload)


@client.event
async def on_reaction_clear_emoji(reaction):
    # TODO remove all reactions for message.id
    print("on_reaction_clear_emoji ", reaction)


@client.event
async def on_raw_reaction_clear_emoji(payload):
    # TODO remove all reactions for message.id
    print("on_raw_reaction_clear_emoji ", payload)

if __name__ == "__main__":
    start_bot()
