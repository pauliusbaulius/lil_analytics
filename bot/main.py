import datetime
import os
from timeit import default_timer
from typing import List

import discord
from discord.ext import commands

from bot import api
from bot.decorators import timer
from bot.root import ROOT_DIR
from bot.utils import is_owner

from bot import models

client = commands.Bot(command_prefix=commands.when_mentioned_or(os.environ["COMMAND_PREFIX"]))
client.remove_command("help")


def start_bot():
    print("lil analytics: Calling start_bot() in main.py!")

    # print("lil analytics: Adding src/ to syspath!")
    # sys.path.insert(0, definitions.root_dir)

    print("lil analytics: Loading cogs.")
    # Load all cogs by default.
    for filename in os.listdir(os.path.join(ROOT_DIR, "cogs")):
        if filename.endswith(".py"):
            cog = f"cogs.{filename[:-3]}"
            client.load_extension(cog)
            print(f"  {cog} loaded!")

    print("lil analytics: Connecting to Discord and starting the client...")
    client.run(os.environ["BOT_TOKEN"])


@client.event
async def on_ready():
    # This runs if everything goes right. Starts background processes.
    await client.change_presence(activity=discord.Game(name=os.environ["STATUS_MESSAGE"]))  # Add status message.
    print("lil analytics: Bot is now running!")

    print("lil analytics: Background indexing of messages in last 24h started!")
    time_before = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    #for guild_id in [g.id for g in client.guilds]:
    #    await client.loop.create_task(background_parse_history(client=client, guild_id=guild_id, after=time_before))


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


@client.event
async def on_message(message):
    """This is where you can add functions that react to user messages that
    are not direct commands. """

    # Prevent recursive calls.
    if message.author == client.user:
        await addmsg(message)
        return

    await addmsg(message)

    # Handle other commands.
    await client.process_commands(message)


@client.event
async def on_bulk_message_delete(messages: List[discord.Message]):
    for message in messages:
        await api.delete_message(message.id)


@client.event
async def on_raw_bulk_message_delete(payload: discord.RawBulkMessageDeleteEvent):
    for message_id in payload.message_ids:
        await api.delete_message(message_id)


@client.event
async def on_message_delete(message: discord.Message):
    await api.delete_message(message.id)


@client.event
async def on_raw_message_delete(payload: discord.RawMessageDeleteEvent):
    await api.delete_message(payload.message_id)


@client.event
async def on_message_edit(_, after):
    # m = models.Message(message_id=after.id,
    #                    author_id=after.author.id,
    #                    channel_id=after.channel.id,
    #                    server_id=after.guild.id,
    #                    date_utc=after.created_at,
    #                    date_last_edited_utc=after.edited_at,
    #                    length=len(after.clean_content),
    #                    #attachments=[x.url for x in after.attachments],
    #                    is_pinned=after.pinned,
    #                    is_everyone_mention=after.mention_everyone,
    #                    is_deleted=0,
    #                    #mentions=list(set(after.raw_mentions)),  # Prevent duplicate spam.
    #                    #channel_mentions=list(set(after.raw_channel_mentions))  # Prevent duplicate spam.
    #                    )
    await addmsg(after)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent):
    # TODO API do not add to db if does not exist? Or try adding...
    d = payload.data
    # print("payload data", d)
    #
    # s = models.Server(id=d["guild_id"],
    #                   name=message.guild.name,
    #                   is_deleted=False,
    #                   owner_id=message.guild.owner_id
    #                   )
    #
    # c = models.Channel(id=d["channel_id"],
    #                    server_id=message.guild.id,
    #                    name=message.channel.name,
    #                    position=message.channel.position,
    #                    is_deleted=False
    #                    )
    #
    # u = models.User(id=["auhtor"]["id"],
    #                 username=d["auhtor"]["username"],
    #                 display_name=d["member"]["nick"],
    #                 is_bot=False
    #                 )
    #
    # await api.add_server(s)
    # await api.add_channel(c)
    # await api.add_user(u)

    try:
        m = models.Message(message_id=payload.message_id,
                           author_id=d["author"]["id"],
                           channel_id=payload.channel_id,
                           server_id=d["guild_id"],
                           date_utc=d.get("timestamp"),
                           date_last_edited_utc=datetime.datetime.utcnow(),
                           length=len(d["content"]),
                           is_pinned=d["pinned"],
                           is_everyone_mention=d["mention_everyone"],
                           is_deleted=False,
                           )
        await api.add_message(m)

        # TODO create attachment model and send data, need to delete old attachments and add those sent!
        attachments = [x.url for x in d["attachments"]]
        # mentions=list(set([int(x["id"]) for x in d["mentions"]])),  # Prevent duplicate spam.
        # channel_mentions=list(set())  # payload has no channel_mentions, just because :)

    except KeyError:
        # Author.id is not found, because bots sending embedded messages create raw_message_edit event with less data,
        # no idea why, but it is what it is.
        pass


@client.event
async def on_reaction_add(reaction, user):
    reaction = models.Reaction(message_id=reaction.message.id,
                               reaction_id=str(reaction.emoji),
                               reaction_hash=hash(str(reaction.emoji)),
                               reacted_id=user.id,
                               is_deleted=False
                               )
    await api.add_reaction(reaction)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    reaction = models.Reaction(message_id=payload.message_id,
                               reaction_id=str(payload.emoji),
                               reaction_hash=hash(str(payload.emoji)),
                               reacted_id=payload.user_id,
                               is_deleted=False
                               )
    await api.add_reaction(reaction)


@client.event
async def on_reaction_remove(reaction, user):
    await api.delete_reaction(message_id=reaction.message.id, reaction_id=reaction.message.author.id, reacted_id=user.id)


@client.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    await api.delete_reaction(payload.message_id, payload.emoji, payload.user_id)


@client.event
async def on_reaction_clear(message, reactions):
    # TODO
    print("on_reaction_clear", message)


@client.event
async def on_raw_reaction_clear(payload):
    # TODO
    print("on_raw_reaction_clear ", payload)


@client.event
async def on_reaction_clear_emoji(reaction):
    # TODO
    print("on_reaction_clear_emoji ", reaction)


@client.event
async def on_raw_reaction_clear_emoji(payload):
    # TODO
    print("on_raw_reaction_clear_emoji ", payload)


# TODO rename, move
async def addmsg(message: discord.Message):
    s = models.Server(id=message.guild.id,
                      name=message.guild.name,
                      is_deleted=False,
                      owner_id=message.guild.owner_id
                      )

    c = models.Channel(id=message.channel.id,
                       server_id=message.guild.id,
                       name=message.channel.name,
                       position=message.channel.position,
                       is_deleted=False
                       )

    u = models.User(id=message.author.id,
                    username=message.author.name,
                    display_name=message.author.display_name,
                    is_bot=message.author.bot
                    )

    await api.add_server(s)
    await api.add_channel(c)
    await api.add_user(u)

    a = [models.Attachment(message_id=message.id, url=x.url) for x in message.attachments]
    for x in a:
        await api.add_attachment(x)

    # TODO do the same with mentions
    mentions = list(set(message.raw_mentions))  # Prevent duplicate spam.
    channel_mentions = list(set(message.raw_channel_mentions))  # Prevent duplicate spam.

    # TODO parse reactions and add to db

    # Add message metadata to database.
    m = models.Message(message_id=message.id,
                       author_id=message.author.id,
                       channel_id=message.channel.id,
                       server_id=message.guild.id,
                       date_utc=message.created_at,
                       date_last_edited_utc=message.edited_at,
                       length=len(message.clean_content),
                       is_pinned=message.pinned,
                       is_everyone_mention=message.mention_everyone,
                       is_deleted=0
                       )
    await api.add_message(m)


async def background_parse_history(client: discord.Client,
                                   guild_id: int,
                                   after: datetime.datetime.date = None) -> tuple:
    """Goes over all channels and indexes messages. Adds missing messages to the database.

    :param client: Discord client object.
    :param guild_id: Id of the guild to be indexed.
    :param after: Index messages up to this day. Default is None, all messages will be indexed.
    :return: Amount of messages indexed and output message to the end user.
    """
    guild = client.get_guild(int(guild_id))
    messages = 0
    channels = []
    for channel in guild.text_channels:
        channels.append(channel.name)
        # Try indexing, if for some reason permissions are missing, just skip that guild.
        try:
            messages += await _parse_channel_history(channel, after)
        except discord.errors.Forbidden:
            # TODO log it as error.
            print(f"Could not index {guild_id} because of missing permissions... Skipping.")
            pass
    return messages, ' '.join(channels)


async def _parse_channel_history(channel: discord.TextChannel, after: datetime.datetime.date = None) -> int:
    """Uses discord.py history method to iterate channel's history from the newest to the oldest message.

    :param channel: Discord channel object to index.
    :param after: Index messages up to this day. Default is None, all messages will be indexed.
    :return: Amount of messages iterated in channel's history.
    """
    message_counter = 0
    async for message in channel.history(limit=None, after=after):
        await addmsg(message)
        message_counter += 1
    return message_counter


@client.command()
async def index(ctx):
    """Indexes all messages in a server that can be read by the bot.

    Goes over all channels and reads history from newest to oldest available message.
    Adds messages and their metadata to the database in 500 message bulk insertions.
    """
    if is_owner(ctx.message.author.id):
        start = default_timer()
        indexed_count, channels = await background_parse_history(client, ctx.guild.id)
        end = default_timer()
        info = f"""
                ```
                indexing done...
                time taken: {str(datetime.timedelta(seconds=end - start))}
                messages processed: {indexed_count}
                channels indexed: {channels}
                ```
                """
        await ctx.send(info)

if __name__ == "__main__":
    start_bot()
