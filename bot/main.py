import datetime
import os
from timeit import default_timer
from typing import List

import discord
from discord.ext import commands

from bot import api, models
from bot.decorators import timer
from bot.root import ROOT_DIR
from bot.utils import is_owner

# Intent is needed to get full list of guild members, without intent guild.members() will only return bot instance!
intents = discord.Intents.default()
intents.presences = True
client = commands.Bot(command_prefix=commands.when_mentioned_or(os.environ["COMMAND_PREFIX"]), intents=intents)
client.remove_command("help")


def start_bot():
    print("lil analytics: Calling start_bot() in main.py!")

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

    print("lil analytics: Indexing channels and members...")
    for guild in client.guilds:
        await client.loop.create_task(background_parse_metadata(guild=guild))

    print("lil analytics: Background indexing of messages started!")
    time_before = datetime.datetime.utcnow() - datetime.timedelta(hours=24)
    for guild_id in [g.id for g in client.guilds]:
        await client.loop.create_task(background_parse_history(client=client, guild_id=guild_id, after=time_before))


@client.command()
async def load(ctx, extension):
    """Loads cog from cogs folder."""
    if is_owner(ctx.message.author.id):
        try:
            client.load_extension(f"cogs.{extension}")
            await ctx.send(f"Loaded extension [{extension}]")
        except ModuleNotFoundError:
            await ctx.send(f"Extension [{extension}] does not exist.")


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


"""
    MESSAGE HANDLING
"""


@client.event
async def on_message(message):
    """
    This is where you can add functions that react to user messages that
    are not direct commands.
    """

    # Prevent recursive calls.
    if message.author == client.user:
        await parse_message(message)
        return

    await parse_message(message)

    # Handle other commands.
    await client.process_commands(message)


@client.event
async def on_message_edit(_, after):
    await parse_message(after)


@client.event
async def on_raw_message_edit(payload: discord.RawMessageUpdateEvent) -> None:
    """
    Creates a message object from payload data. Sends message to the api to be updated/inserted into the database.
    Requests to delete all attachment data, to not make a request and compare data. Sends new attachment data instead.
    """
    d = payload.data

    try:
        m = models.Message(
            message_id=payload.message_id,
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
        attachments = [x["url"] for x in d["attachments"]]
        if len(attachments) > 0:
            for attachment in attachments:
                # Should delete old attachments before adding new ones!
                await api.delete_attachments(message_id=payload.message_id)
                await api.add_attachment(models.Attachment(message_id=payload.message_id, url=attachment[0]))

    except KeyError:
        # Author.id is not found, because bots sending embedded messages create raw_message_edit event with less data,
        # no idea why, but it is what it is.
        pass


async def parse_message(message: discord.Message):
    """
    Given a message object, extracts data to build model of Message.
    """
    # s = models.Server(
    #     id=message.guild.id,
    #     name=message.guild.name,
    #     is_deleted=False,
    #     owner_id=message.guild.owner_id,
    # )
    #
    # c = models.Channel(
    #     id=message.channel.id,
    #     server_id=message.guild.id,
    #     name=message.channel.name,
    #     position=message.channel.position,
    #     is_deleted=False,
    # )
    #
    # u = models.User(
    #     id=message.author.id,
    #     username=message.author.name,
    #     display_name=message.author.display_name,
    #     is_bot=message.author.bot,
    # )
    #
    # await api.add_server(s)
    # await api.add_channel(c)
    # await api.add_user(u)

    a = [models.Attachment(message_id=message.id, url=x.url) for x in message.attachments]
    for x in a:
        await api.add_attachment(x)

    for reaction in message.reactions:
        r = models.Reaction(
            message_id=message.id,
            reaction_id=str(reaction.emoji),
            reaction_hash=hash(str(reaction.emoji)),
            reacted_id=message.author.id,
            is_deleted=False,
        )
        await api.add_reaction(reaction=r)

    # Add message metadata to database.
    m = models.Message(
        message_id=message.id,
        author_id=message.author.id,
        channel_id=message.channel.id,
        server_id=message.guild.id,
        date_utc=message.created_at,
        date_last_edited_utc=message.edited_at,
        length=len(message.clean_content),
        is_pinned=message.pinned,
        is_everyone_mention=message.mention_everyone,
        is_deleted=0,
    )
    await api.add_message(m)


@client.event
async def on_guild_channel_update(before, after):
    c = models.Channel(
        id=after.id,
        server_id=after.guild.id,
        name=after.name,
        position=after.position,
        is_deleted=False,
    )
    await api.add_channel(c)


@client.event
async def on_member_update(before, after):
    u = models.User(
        id=after.id,
        username=after.name,
        display_name=after.display_name,
        is_bot=after.bot,
    )
    await api.add_user(u)


@client.event
async def on_guild_update(before, after):
    # TODO new fields! url, amouunt of voice channels,  https://discordpy.readthedocs.io/en/latest/api.html?highlight=guild%20channels#discord.abc.GuildChannel
    s = models.Server(
        id=after.id,
        name=after.name,
        is_deleted=False,
        owner_id=after.owner_id,
    )
    await api.add_server(s)


@client.event
async def on_reaction_add(reaction, user):
    reaction = models.Reaction(
        message_id=reaction.message.id,
        reaction_id=str(reaction.emoji),
        reaction_hash=hash(str(reaction.emoji)),
        reacted_id=user.id,
        is_deleted=False,
    )
    await api.add_reaction(reaction)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    reaction = models.Reaction(
        message_id=payload.message_id,
        reaction_id=str(payload.emoji),
        reaction_hash=hash(str(payload.emoji)),
        reacted_id=payload.user_id,
        is_deleted=False,
    )
    await api.add_reaction(reaction)


@client.event
async def on_reaction_remove(reaction, user):
    await api.delete_reaction(
        message_id=reaction.message.id,
        reaction_id=reaction.message.author.id,
        reacted_id=user.id,
    )


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


@client.event
async def on_guild_channel_delete(channel: discord.abc.GuildChannel):
    """
    Sends channel delete request to the api.
    """
    await api.delete_channel(channel_id=channel.id)


async def background_parse_metadata(guild: discord.Guild):
    """
    On boot, indexes all guilds, channels and users. Updates/inserts new data into the database via api calls.
    This is needed to get new changes on start, when bot is live, on_*_update functions do this job instead.
    """
    s = models.Server(
        id=guild.id,
        name=guild.name,
        is_deleted=False,
        owner_id=guild.owner_id,
    )
    await api.add_server(s)

    for channel in guild.text_channels:
        c = models.Channel(
            id=channel.id,
            server_id=guild.id,
            name=channel.name,
            position=channel.position,
            is_deleted=False,
        )
        await api.add_channel(c)

    async for user in guild.fetch_members(limit=None):
        u = models.User(
            id=user.id,
            username=user.name,
            display_name=user.display_name,
            is_bot=user.bot,
        )
        await api.add_user(u)


async def background_parse_history(
    client: discord.Client, guild_id: int, after: datetime.datetime.date = None
) -> tuple:
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
    return messages, " ".join(channels)


async def _parse_channel_history(channel: discord.TextChannel, after: datetime.datetime.date = None) -> int:
    """Uses discord.py history method to iterate channel's history from the newest to the oldest message.

    :param channel: Discord channel object to index.
    :param after: Index messages up to this day. Default is None, all messages will be indexed.
    :return: Amount of messages iterated in channel's history.
    """
    message_counter = 0
    async for message in channel.history(limit=None, after=after):
        await parse_message(message)
        message_counter += 1
    return message_counter


@client.command()
async def index(ctx):
    """Indexes all messages in a server that can be read by the bot.

    Goes over all channels and reads history from newest to oldest available message.
    Adds messages and their metadata to the database in 500 message bulk insertions.
    """
    if is_owner(ctx.message.author.id):
        await ctx.send("`lil_analytics@matrix: indexing started!`")
        start = default_timer()
        indexed_count, channels = await background_parse_history(client=client, guild_id=ctx.guild.id)
        end = default_timer()
        info = f"""```\nlil_analytics@matrix:\n indexing done...\n time taken: {str(datetime.timedelta(seconds=end - start))}\n messages processed: {indexed_count}\n channels indexed: {channels}```"""
        await ctx.send(info)
    else:
        await ctx.send(ctx.message.author.id)


@client.event
async def on_guild_join(guild):
    # When bot joins a guild, messages of past 14 days are indexed!
    time_before = datetime.datetime.utcnow() - datetime.timedelta(days=14)
    await background_parse_history(client=client, guild_id=guild.id, after=time_before)


@client.event
async def on_guild_remove(guild):
    await api.delete_server(server_id=guild.id)

if __name__ == "__main__":
    start_bot()
