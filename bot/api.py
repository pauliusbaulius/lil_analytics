"""
Communication with the API. add_ should be used to update information. MongoDB can "upsert".
"""
from . import models
import requests


async def add_user(user: models.User):
    try:
        r = requests.post(url="http://api:5000/user/", data=user.json())
    except AttributeError:
        print(user)


async def add_server(server: models.Server):
    try:
        r = requests.post(url="http://api:5000/server/", data=server.json())
    except AttributeError:
        print(server)


async def add_channel(channel: models.Channel):
    try:
        r = requests.post(url="http://api:5000/channel/", data=channel.json())
    except AttributeError:
        print(channel)


async def add_message(message: models.Message):
    try:
        r = requests.post(url="http://api:5000/message/", data=message.json())
    except AttributeError:
        print(message)


async def add_reaction(reaction: models.Reaction):
    try:
        r = requests.post(url="http://api:5000/reaction/", data=reaction.json())
    except AttributeError:
        print(reaction)


async def delete_message(message_id: int):
    """
    Called by on_message_delete, on_bulk_message_delete, on_raw_bulk_message_delete, on_raw_message_delete
    """
    r = requests.delete(url="http://api:5000/message/", data={"message_id": message_id})


async def delete_reaction(message_id: int, reaction_id: str, reacted_id: int):
    """
    To delete a reaction, 3 parameters are required! Which message, what reaction and who added it.
    Uses soft-delete.
    """
    r = models.Reaction(message_id=message_id,
                        reacted_id=reacted_id,
                        reaction_id=str(reaction_id),
                        reaction_hash=hash(str(reaction_id)),
                        is_deleted=True)
    await add_reaction(r)


async def delete_reactions(message_id: int):
    """
    Option to clear all reactions!
    """
    print("api.delete_reactions", message_id)


async def add_attachment(a: models.Attachment):
    try:
        r = requests.post(url="http://api:5000/attachment/", data=a.json())
        print(r.json())
    except AttributeError:
        print(a)