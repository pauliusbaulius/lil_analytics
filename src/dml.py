import datetime
import re

import discord

from src.decorators import timer
import src.sqlite as sqlite


"""
    This is the place where message metadata goes in, gets butchered and then inserted into the database.
    There are 8 tables at the moment. Database is build with build_database() function.
"""


@timer
async def add_message(message: discord.Message):
    """Given a message object, inserts relevant data into the database."""
    cn = sqlite.db_connection
    c = sqlite.db_cursor

    # Add channel data.
    sql = """INSERT OR REPLACE INTO channels VALUES (? ,?, ?, ?)"""
    to_insert = (message.channel.id, message.guild.id, message.channel.name, 0)
    c.execute(sql, to_insert)

    # Add message data.
    sql = """INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    # Add the magic +00:00 that discord just doesnt do.
    date = message.created_at.isoformat() + '+00:00'
    try:
        date_edited = message.edited_at.isoformat() + '+00:00'
    except AttributeError:
        date_edited = None

    to_insert = (message.id, message.guild.id, message.channel.id, message.author.id, message.author.name,
                 len(message.clean_content), date, date_edited, message.author.bot, message.pinned,
                 len(message.attachments), len(message.embeds), message.mention_everyone, 0)
    c.execute(sql, to_insert)

    cn.commit()

    await add_message_metadata(message.id, message.mentions, message.channel_mentions, message.role_mentions,
                               message.reactions)


async def add_message_bulk(messages: list):
    """Given a message object, inserts relevant data into the database."""
    cn = sqlite.db_connection
    c = sqlite.db_cursor

    sql_channels = """INSERT OR REPLACE INTO channels VALUES (? ,?, ?, ?)"""
    sql_messages = """INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    to_insert_channels = []
    to_insert_messages = []
    for message in messages:
        to_insert_channels.append((message.channel.id, message.guild.id, message.channel.name, 0))

        # Add the magic +00:00 that discord just doesnt do.
        date = message.created_at.isoformat() + '+00:00'
        try:
            date_edited = message.edited_at.isoformat() + '+00:00'
        except AttributeError:
            date_edited = None

        to_insert_messages.append((message.id, message.guild.id, message.channel.id, message.author.id, message.author.name,
                     len(message.clean_content), date, date_edited, message.author.bot, message.pinned,
                     len(message.attachments), len(message.embeds), message.mention_everyone, 0))

    c.executemany(sql_channels, to_insert_channels)
    c.executemany(sql_messages, to_insert_messages)

    cn.commit()

    await add_message_metadata_bulk(messages)


@timer
async def add_message_metadata_bulk(messages: list):
    user_mentions = []
    channel_mentions = []
    role_mentions = []
    message_ids = []
    for message in messages:
        message_ids.append((message.id,))
        [user_mentions.append((message.id, user_id.id)) for user_id in message.mentions]
        [channel_mentions.append((message.id, channel_id.id)) for channel_id in message.channel_mentions]
        [role_mentions.append((message.id, role_id.id)) for role_id in message.role_mentions]

    cn = sqlite.db_connection
    c = sqlite.db_cursor

    # Delete "old" metadata to reduce checking.
    c.executemany('DELETE FROM user_mentions WHERE id == ?', message_ids)
    c.executemany('DELETE FROM channel_mentions WHERE id == ?', message_ids)
    c.executemany('DELETE FROM role_mentions WHERE id == ?', message_ids)

    # Insert new metadata.
    c.executemany('INSERT OR IGNORE INTO user_mentions VALUES (?, ?)', user_mentions)
    c.executemany('INSERT OR IGNORE INTO channel_mentions VALUES (?, ?)', channel_mentions)
    c.executemany('INSERT OR IGNORE INTO role_mentions VALUES (?, ?)', role_mentions)

    cn.commit()

    await add_reactions_bulk(messages)

@timer
async def add_reactions_bulk(messages: list):

    reactions = []
    message_ids = []
    for message in messages:
        message_ids.append((message.id, ))
        for reaction in message.reactions:
            [reactions.append((reaction.message.id, str(reaction.emoji), user.id, hash(str(reaction.emoji)))) for user in await reaction.users().flatten()]

    cn = sqlite.db_connection
    c = sqlite.db_cursor
    # Delete current reactions
    c.executemany('DELETE FROM message_reactions WHERE id == ?', message_ids)
    # Insert new reactions.
    c.executemany('INSERT INTO message_reactions VALUES (?, ?, ?, ?)', reactions)
    cn.commit()


@timer
async def add_message_metadata(message_id: int, user_mentions: list, channel_mentions: list, role_mentions: list,
                               reactions):
    """Inserts message metadata into database. Deletes old metadata first to
    prevent conflicts.

    This also prevents mixup of data, since all data is saved for
    current message state and deleted for old message state. Efficient?
    Not really. But it does not have to query and compare messages.
    """

    # Prepare metadata
    user_mentions = [(message_id, user_id.id) for user_id in user_mentions]
    channel_mentions = [(message_id, channel_id.id) for channel_id in channel_mentions]
    role_mentions = [(message_id, role_id.id) for role_id in role_mentions]

    cn = sqlite.db_connection
    c = sqlite.db_cursor

    # Delete "old" metadata to reduce checking.
    c.execute('DELETE FROM user_mentions WHERE id == ?', (message_id,))
    c.execute('DELETE FROM channel_mentions WHERE id == ?', (message_id,))
    c.execute('DELETE FROM role_mentions WHERE id == ?', (message_id,))

    # Insert new metadata.
    c.executemany('INSERT OR IGNORE INTO user_mentions VALUES (?, ?)', user_mentions)
    c.executemany('INSERT OR IGNORE INTO channel_mentions VALUES (?, ?)', channel_mentions)
    c.executemany('INSERT OR IGNORE INTO role_mentions VALUES (?, ?)', role_mentions)

    cn.commit()

    for reaction in reactions:
        await add_reactions(reaction)


@timer
async def message_bulk_delete(message_ids: list):
    """Given a list of message ids, soft deletes those messages in the database by setting deleted=1.

    Discord might send a list of discord.Message ids but it can also send message objects.

    Arguments:
        message_ids: A list of discord.Message ids or message objects.
    """
    # TODO add message to db if does not exist!
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    for message_id in message_ids:
        if isinstance(message_id, int):
            c.execute('UPDATE messages SET deleted = 1 WHERE id == ?', (message_id,))
        else:
            c.execute('UPDATE messages SET deleted = 1 WHERE id == ?', (message_id.id,))
    cn.commit()


@timer
async def message_delete(message_id: int):
    """Given a message id, soft deletes given message by setting it's deleted column to 1.

    Arguments:
        message_id: A discord.Message id.
    """
    # TODO add message to db if does not exist!
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('UPDATE messages SET deleted = 1 WHERE id == ?', (message_id,))
    cn.commit()


@timer
async def message_update(message: discord.Message = None, message_raw: discord.RawMessageUpdateEvent = None):
    """Given a normal discord message or raw message update event, updates
    message metadata in the database."""
    if message:
        await add_message(message)
    elif message_raw:
        try:
            data = message_raw.data

            # Add the magic +00:00 that discord just doesnt do.
            date = data['timestamp'] + '+00:00'
            try:
                date_edited = data['edited_timestamp'].isoformat() + '+00:00'
            except AttributeError:
                date_edited = None

            values = (data['id'], data['guild_id'], data['channel_id'], data['author']['id'],
                      data['author']['username'], len(data['content']), date, date_edited,
                      data['author']['public_flags'], data['pinned'], len(data['attachments']), len(data['embeds']),
                      data['mention_everyone'], 0)

            cn = sqlite.db_connection
            c = sqlite.db_cursor
            c.execute('INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
            cn.commit()

            # Handle metadata.
            user_mentions = [x['id'] for x in data['mentions']]
            role_mentions = data['mention_roles']
            # For some reason they do not give you mentioned channels?
            # So I have to extract them with regex, like some kind of an animal.
            # Find all channel mentions and strip <# > and remove duplicates.
            channel_mentions = [x[2:-1] for x in set(re.findall(re.compile('<#\d{18}>'), data['content']))]
            await add_message_metadata(data['id'], user_mentions, channel_mentions, role_mentions, data['reactions'])

        except KeyError:
            # RawMessageUpdateEvent also triggered when you post image or url in embeds, need to ignore that.
            pass


@timer
async def add_reactions(reaction: discord.Reaction):
    """Given reaction object, adds relevant data to the database."""
    values = [(reaction.message.id, str(reaction.emoji), user.id, hash(str(reaction.emoji)))
              for user
              in await reaction.users().flatten()]

    cn = sqlite.db_connection
    c = sqlite.db_cursor
    # Delete current reactions
    c.execute('DELETE FROM message_reactions WHERE id == ?', (reaction.message.id,))
    # Insert new reactions.
    c.executemany('INSERT INTO message_reactions VALUES (?, ?, ?, ?)', values)
    cn.commit()


async def add_reaction_raw(message_id: int, reaction_id, reacted_id: int):
    """Given message, reaction and user which reacted ids, creates an entry in
    the database."""
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('INSERT OR IGNORE INTO message_reactions VALUES (?, ?, ?, ?)', (message_id, str(reaction_id),
                                                                              reacted_id, hash(str(reaction_id))))
    cn.commit()


@timer
async def add_reaction(reaction: discord.Reaction, reacted_id: int):
    await add_reaction_raw(reaction.message.id, reaction.emoji, reacted_id)


@timer
async def remove_reaction_raw(message_id: int, reaction_id, reacted_id: int):
    """Given a message id and other data needed to construct a key, deletes
    reactions from database matching the key."""
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('DELETE FROM message_reactions WHERE id == ? AND reaction_id == ? AND reacted_id == ?',
              (message_id, str(reaction_id), reacted_id))
    cn.commit()


@timer
async def remove_reaction(reaction: discord.Reaction, reacted_id: int):
    await remove_reaction_raw(reaction.message.id, reaction.emoji, reacted_id)


@timer
async def reaction_clear(message: discord.Message, reactions):
    # TODO delete reactions for that message
    print('db_reactions_clear', message, reactions)
    message_id = None
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('DELETE FROM message_reactions WHERE id == ?',
              (message_id,))
    cn.commit()


@timer
async def reaction_clear_raw(payload: discord.RawReactionClearEvent):
    # TODO delete reactions for that message
    print('db_reactions_clear_raw', payload)
    message_id = None
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('DELETE FROM message_reactions WHERE id == ?',
              (message_id,))
    cn.commit()


@timer
async def background_parse_history(client: discord.Client, guild_id: int):
    """Goes over all channels and parses yet non-parsed messages."""
    guild = client.get_guild(int(guild_id))
    messages = 0
    channels = []
    for channel in guild.text_channels:
        channels.append(channel.name)
        messages += await _parse_channel_history(channel)
    return messages, ' '.join(channels)


@timer
async def _parse_channel_history(channel: discord.TextChannel) -> int:
    """Uses discord.py history method to iterate channel's history from the newest to the oldest message.

    :param channel: Discord channel object to index.
    :return: Amount of messages iterated in channel's history.
    """
    messages = []
    message_counter = 0
    async for message in channel.history(limit=None):
        messages.append(message)
        message_counter += 1
        # Insert every 500 messages! This uses db connection every 500 messages instead of every single one!
        if message_counter % 500 == 0:
            await add_message_bulk(messages)
            messages.clear()
    # Insert remaining messages.
    if messages:
        await add_message_bulk(messages)

    return message_counter


@timer
def add_reply(text: str):
    """Adds a new reply to bot_replies for bot to use.

    Arguments:
        text: Bot reply to add
    """
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    now = datetime.datetime.now().isoformat()
    c.execute('INSERT INTO bot_replies VALUES (?, ?)', (text, now))
    cn.commit()


@timer
def get_reply() -> str:
    """Returns a random reply from bot_replies if there are any, otherwise it returns None.

    Returns:
        A single reply from bot_replies table in the database.
    """
    cn = sqlite.db_connection
    c = sqlite.db_cursor
    c.execute('SELECT message FROM bot_replies ORDER BY random() LIMIT 1')
    reply = c.fetchone()[0]
    return reply
