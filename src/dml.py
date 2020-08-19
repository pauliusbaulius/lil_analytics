import datetime
import re
import sqlite3

import discord

from src.utils import get_database


"""
    This is the place where message metadata goes in, gets butchered and then inserted into the database.
    There are 8 tables at the moment. Database is build with build_database() function.
"""


async def add_message(message: discord.Message):
    """Given a message object, inserts relevant data into the database."""
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()

        # Add channel data.
        sql = """INSERT OR REPLACE INTO channels VALUES (? ,?, ?)"""
        to_insert = (message.channel.id, message.guild.id, message.channel.name)
        c.execute(sql, to_insert)

        # Add message data.
        sql = """INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

        # Add the magic +00:00 that discord just doesnt do.
        date = message.created_at.isoformat() + '+00:00'
        try:
            date_edited = message.edited_at.isoformat() + '+00:00'
        except AttributeError:
            date_edited = None

        to_insert = (message.id, message.guild.id, message.channel.id, message.author.id, message.author.name,
                     len(message.clean_content), date, date_edited, message.author.bot, message.pinned,
                     len(message.attachments), len(message.embeds), message.mention_everyone)
        c.execute(sql, to_insert)

        cn.commit()

        await add_message_metadata(message.id, message.mentions, message.channel_mentions, message.role_mentions,
                                   message.reactions)


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

    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('PRAGMA foreign_keys = ON')

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


async def message_bulk_delete(message_ids: list):
    """Given a list of message ids, deletes those messages in the database.

    Discord might send a list of discord.Message ids but it can also send message objects.

    Arguments:
        message_ids: A list of discord.Message ids or message objects.
    """
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('PRAGMA foreign_keys = ON')
        for message_id in message_ids:
            if isinstance(message_id, int):
                c.execute('DELETE FROM messages WHERE id == ?', (message_id,))
            else:
                c.execute('DELETE FROM messages WHERE id == ?', (message_id.id,))
        cn.commit()


async def message_delete(message_id: int):
    """Give a single message id, it is removed from the database.

    Arguments:
        message_id: A discord.Message id.
    """
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('PRAGMA foreign_keys = ON')
        c.execute('DELETE FROM messages WHERE id == ?', (message_id,))
        cn.commit()


async def message_update(message: discord.Message = None, message_raw: discord.RawMessageUpdateEvent = None):
    """Given a normal discord message or raw message update event, updates
    message metadata in the datbase."""
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
                      data['mention_everyone'])

            with sqlite3.connect(get_database()) as cn:
                c = cn.cursor()
                c.execute('INSERT OR REPLACE INTO messages VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', values)
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


async def add_reactions(reaction: discord.Reaction):
    """Given reaction object, adds relevant data to the database."""
    values = [(reaction.message.id, str(reaction.emoji), user.id, hash(str(reaction.emoji)))
              for user
              in await reaction.users().flatten()]

    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        # Delete current reactions
        c.execute('DELETE FROM message_reactions WHERE id == ?', (reaction.message.id,))
        # Insert new reactions.
        c.executemany('INSERT INTO message_reactions VALUES (?, ?, ?, ?)', values)
        cn.commit()


async def add_reaction_raw(message_id: int, reaction_id, reacted_id: int):
    """Given message, reaction and user which reacted ids, creates an entry in
    the database."""
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('INSERT OR IGNORE INTO message_reactions VALUES (?, ?, ?, ?)', (message_id, str(reaction_id),
                                                                                  reacted_id, hash(str(reaction_id))))
        cn.commit()


async def add_reaction(reaction: discord.Reaction, reacted_id: int):
    await add_reaction_raw(reaction.message.id, reaction.emoji, reacted_id)


async def remove_reaction_raw(message_id: int, reaction_id, reacted_id: int):
    """Given a message id and other data needed to construct a key, deletes
    reactions from database matching the key."""
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('DELETE FROM message_reactions WHERE id == ? AND reaction_id == ? AND reacted_id == ?',
                  (message_id, str(reaction_id), reacted_id))
        cn.commit()


async def remove_reaction(reaction: discord.Reaction, reacted_id: int):
    await remove_reaction_raw(reaction.message.id, reaction.emoji, reacted_id)


async def reaction_clear(message: discord.Message, reactions):
    # TODO delete reactions for that message
    print('db_reactions_clear', message, reactions)
    message_id = None
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('DELETE FROM message_reactions WHERE id == ?',
                  (message_id,))
        cn.commit()


async def reaction_clear_raw(payload: discord.RawReactionClearEvent):
    # TODO delete reactions for that message
    print('db_reactions_clear_raw', payload)
    message_id = None
    with sqlite3.connect(get_database()) as cn:
        c = cn.cursor()
        c.execute('DELETE FROM message_reactions WHERE id == ?',
                  (message_id,))
        cn.commit()


async def background_parse_history(client: discord.Client, guild_id: int):
    """Goes over all channels and parses yet non-parsed messages."""
    # TODO log this function to file: channel: time taken with guild_id and channel info!
    guild = client.get_guild(int(guild_id))
    messages = 0
    channels = []
    for channel in guild.text_channels:
        print(f"parsing {channel.name}")
        channels.append(channel.name)
        messages += await _parse_channel_history(channel)
        print(f"parsed {channel.name}")
    return messages, ' '.join(channels)


async def _parse_channel_history(channel: discord.TextChannel) -> int:
    message_counter = 0
    async for message in channel.history(limit=None, oldest_first=True):
        await add_message(message)
        message_counter += 1
    return message_counter


def add_reply(text: str):
    """Adds a new reply to bot_replies for bot to use.

    Arguments:
        text: Bot reply to add
    """
    with sqlite3.connect(get_database()) as cn:
        cursor = cn.cursor()
        now = datetime.datetime.now().isoformat()
        cursor.execute('INSERT INTO bot_replies VALUES (?, ?)', (text, now))
        cn.commit()


def get_reply() -> str:
    """Returns a random reply from bot_replies if there are any, otherwise it returns None.

    Returns:
        A single reply from bot_replies table in the database.
    """
    with sqlite3.connect(get_database()) as cn:
        cursor = cn.cursor()
        cursor.execute('SELECT message FROM bot_replies ORDER BY random() LIMIT 1')
        reply = cursor.fetchone()[0]
    return reply
