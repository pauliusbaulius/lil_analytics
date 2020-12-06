"""
Communication with the API.
# TODO add_ methods should convert discord object to our model and pass it to send_ method.
#  add_ should be used to update information. MongoDB can "upsert".
# TODO delete_ methods should send request to delete matching id.
"""

from src import models


async def add_user(user: models.User):
    print("api.add_user", user)


async def add_server(server: models.Server):
    print("api.add_server", server)


async def add_channel(channel: models.Channel):
    print("api.add_channel", channel)


async def add_message(message):
    m = models.Message(message_id=message.id,
                       author_id=message.author.id,
                       channel_id=message.channel.id,
                       server_id=message.guild.id,
                       date_utc=message.created_at,
                       date_last_edited_utc=message.edited_at,
                       length=len(message.clean_content),
                       attachments=[x.url for x in message.attachments],
                       is_bot=message.author.bot,
                       is_pinned=message.pinned,
                       is_everyone_mention=message.mention_everyone,
                       is_deleted=0,
                       mentions=list(set(message.raw_mentions)), # Prevent duplicate spam.
                       channel_mentions=list(set(message.raw_channel_mentions)) # Prevent duplicate spam.
                       )
    s = models.Server(server_id=message.guild.id,
                      name=message.guild.name,
                      is_deleted=0,
                      owner_id=message.guild.owner_id
                      )
    c = models.Channel(channel_id=message.channel.id,
                       server_id=message.guild.id,
                       name=message.channel.name,
                       position=message.channel.position,
                       is_deleted=0
                       )
    u = models.User(user_id=message.author.id,
                    name=message.author.name,
                    display_name=message.author.display_name,)
    print(m, s, c, u)


async def add_reaction(reaction: models.Reaction):
    print("api.add_reaction", reaction)


async def delete_message(message_id: int):
    """

    Called by on_message_delete, on_bulk_message_delete, on_raw_bulk_message_delete, on_raw_message_delete
    """
    print("api.delete_message", message_id)


async def delete_reaction(message_id: int, reaction_id: int, reacted_id: int):
    """
    To delete a reaction, 3 parameters are required! Which message, what reaction and who added it.

    """
    print("api.delete_reaction", message_id, reaction_id, reacted_id)


async def delete_reactions(message_id: int):
    """
    Option to clear all reactions!
    """
    print("api.delete_reactions", message_id)

