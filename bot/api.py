"""
Communication with the API. add_ should be used to update information. MongoDB can "upsert".
"""

from . import models


async def add_user(user: models.User):
    print("api.add_user")


async def add_server(server: models.Server):
    print("api.add_server")


async def add_channel(channel: models.Channel):
    print("api.add_channel")


async def add_message(message: models.Message):
    try:
        print(message.json())
    except AttributeError:
        print(message)


async def add_reaction(reaction: models.Reaction):
    print("api.add_reaction", reaction)


async def delete_message(message_id: int):
    """
    Called by on_message_delete, on_bulk_message_delete, on_raw_bulk_message_delete, on_raw_message_delete
    """
    # TODO FASTAPI: Check if message exists, if it does, set is_deleted=True
    # api/message/delete/2191930 -> deletes if exists
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

