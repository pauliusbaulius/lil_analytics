"""
Communication with the API. add_ should be used to update information. MongoDB can "upsert".
"""
import requests

from . import models

async def add_server(server: models.Server):
    try:
        _ = requests.post(url="http://api:5000/server/", data=server.json())
    except AttributeError:
        print(server)

async def add_channel(channel: models.Channel):
    try:
        _ = requests.post(url="http://api:5000/channel/", data=channel.json())
    except AttributeError:
        print(channel)


async def add_user(user: models.User):
    try:
        r = requests.post(url="http://api:5000/user/", data=user.json())
    except AttributeError:
        print(r.json())


async def add_message(message: models.Message):
    try:
        r = requests.post(url="http://api:5000/message/", data=message.json())
    except AttributeError:
        print(r.json())


async def delete_message(message_id: int):
    """
    Called by on_message_delete, on_bulk_message_delete, on_raw_bulk_message_delete, on_raw_message_delete
    """
    _ = requests.delete(url=f"http://api:5000/message/?message_id={message_id}")


async def add_attachment(a: models.Attachment):
    try:
        _ = requests.post(url="http://api:5000/attachment/", data=a.json())
    except AttributeError:
        print(a)


async def delete_attachments(message_id: int):
    _ = requests.delete(url=f"http://api:5000/attachment/?message_id={message_id}")


async def add_reaction(reaction: models.Reaction):
    try:
        _ = requests.post(url="http://api:5000/reaction/", data=reaction.json())
    except AttributeError:
        print(reaction)


async def delete_reaction(message_id: int, reaction_id: str, reacted_id: int):
    """
    To delete a reaction, 3 parameters are required! Which message, what reaction and who added it.
    Uses soft-delete.
    """
    r = models.Reaction(
        message_id=message_id,
        reacted_id=reacted_id,
        reaction_id=str(reaction_id),
        reaction_hash=hash(str(reaction_id)),
        is_deleted=True,
    )
    await add_reaction(r)


async def delete_reactions(message_id: int):
    """
    Option to clear all reactions!
    """
    print("api.delete_reactions", message_id)


async def delete_channel(channel_id: int):
    _ = requests.delete(url=f"http://api:5000/channel/?channel_id={channel_id}")
