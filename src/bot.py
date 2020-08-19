import logging
import os

import discord
from discord.ext import commands

import src.ddl
import src.dml as db
import definitions
from src.decorators import timer
from src.utils import find_word, is_owner

# Load bot prefix from settings.json
client = commands.Bot(command_prefix=commands.when_mentioned_or(definitions.command_prefix))
client.remove_command("help")


def start_bot():
    src.ddl.build_database()

    # Load all cogs by default.
    for filename in os.listdir(os.path.join(definitions.root_dir, "src/cogs/")):
        if filename.endswith(".py"):
            client.load_extension(f"cogs.{filename[:-3]}")

    # Start background tasks
    # client.loop.create_task(background_parser())

    # Start client
    client.run(definitions.bot_token)


@client.event
async def on_ready():
    """This runs if everything goes right."""
    await client.change_presence(activity=discord.Game(name=definitions.status_message))
    print("lil_analytics: bot is now running!")


@timer
@client.command()
async def load(ctx, extension):
    """Loads cog from cogs folder."""
    logging.info(
        f"[{ctx.message.author.name}][{ctx.message.author.id}] trying to load [{extension}] cog.")
    if is_owner(ctx.message.author.id):
        try:
            client.load_extension(f"cogs.{extension}")
            await ctx.send(f"Loaded extension [{extension}]")
            logging.info(
                f"[{ctx.message.author.name}][{ctx.message.author.id}] loaded [{extension}] cog.")
        except ModuleNotFoundError:
            await ctx.send(f"Extension [{extension}] does not exist.")
            logging.info(
                f"[{ctx.message.author.name}][{ctx.message.author.id}] cog [{extension}] does not exist.")
    else:
        await ctx.send(f"You can't do this.")
        logging.info(
            f"[{ctx.message.author.name}][{ctx.message.author.id}] is not the owner.")


@timer
@client.command()
async def unload(ctx, extension):
    """Unloads cog from cogs folder."""
    logging.info(
        f"[{ctx.message.author.name}][{ctx.message.author.id}] trying to unload [{extension}] cog.")
    if is_owner(ctx.message.author.id):
        try:
            client.unload_extension(f"cogs.{extension}")
            await ctx.send(f"Unloaded extension [{extension}]")
            logging.info(
                f"[{ctx.message.author.name}][{ctx.message.author.id}] unloaded [{extension}] cog.")
        except ModuleNotFoundError:
            await ctx.send(f"Extension [{extension}] does not exist.")
            logging.info(
                f"[{ctx.message.author.name}][{ctx.message.author.id}] cog [{extension}] does not exist.")
    else:
        await ctx.send(f"You can't do this.")
        logging.info(
            f"[{ctx.message.author.name}][{ctx.message.author.id}] is not the owner.")


@client.event
async def on_message(message):
    """This is where you can add functions that react to user messages that
    are not direct commands. """

    # Prevent recursive calls.
    if message.author == client.user:
        await db.add_message(message)
        return

    # Check if message contains word "bot" or mentions this bot. Reply with a
    # message if true.
    if find_word(message.content.lower(), "lil analytics"):# or is_me(message.mentions):
        reply = db.get_reply()
        await message.channel.send(reply)

    # Add message metadata to database.
    await db.add_message(message)

    # Handle other commands.
    await client.process_commands(message)


@client.event
async def on_member_update(before, after):
    """User activity tracking goes here.
    Currently tracking Spotify listening activity.
    """
    for activity in after.activities:
        if activity.type is discord.ActivityType.listening:
            pass


@client.event
async def on_bulk_message_delete(messages):
    await db.message_bulk_delete(messages)


@client.event
async def on_raw_bulk_message_delete(
        payload: discord.RawBulkMessageDeleteEvent):
    """Discord gives minimal amount of data, this will create holes in
    database if the server was not parsed with .parse_history first!"""
    await db.message_bulk_delete(payload.message_ids)


@client.event
async def on_message_delete(message):
    """Updates database metadata for message.
    Basically sets flag that message is gone and when it was deleted.
    """
    await db.message_delete(message.id)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    """Discord gives minimal amount of data, this will create holes in
    database if the server was not parsed with .parse_history first!"""
    await db.message_delete(payload.message_id)


@client.event
async def on_message_edit(before, after):
    """Updates database metadata for message."""
    await db.message_update(message=after)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    await db.message_update(message_raw=payload)


@client.event
async def on_reaction_add(reaction, user):
    """Updates database metadata for user reactions."""
    await db.add_reaction(reaction, user.id)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Updates database metadata for user reactions."""
    await db.add_reaction_raw(payload.message_id, payload.emoji, payload.user_id)


@client.event
async def on_reaction_remove(reaction, user):
    """Updates database metadata for user reactions."""
    await db.remove_reaction(reaction, user.id)


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Updates database metadata for user reactions."""
    await db.remove_reaction_raw(payload.message_id, payload.emoji, payload.user_id)


@client.event
async def on_reaction_clear(message, reactions):
    """Updates database metadata for user reactions."""
    await db.db_reaction_clear(message, reactions)


@client.event
async def on_raw_reaction_clear(payload):
    await db.db_reaction_clear_raw(payload)


@client.event
async def on_reaction_clear_emoji(reaction):
    # TODO remove all reactions for message.id
    print("on_reaction_clear_emoji ", reaction)


@client.event
async def on_raw_reaction_clear_emoji(payload):
    # TODO remove all reactions for message.id
    print("on_raw_reaction_clear_emoji ",payload)
