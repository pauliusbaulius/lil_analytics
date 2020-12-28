import os

import requests

from . import models

# FIXME this is a shit quality solution. Should send api key with the request, not in url parameter!
API_KEY = f"?api_key={os.environ['FASTAPI_KEY']}"


async def add_server(server: models.Server):
    try:
        _ = requests.post(url="http://api:5000/server/" + API_KEY, data=server.json())
    except AttributeError:
        print(server)


async def add_channel(channel: models.Channel):
    try:
        _ = requests.post(url="http://api:5000/channel/" + API_KEY, data=channel.json())
    except AttributeError:
        print(channel)


async def add_user(user: models.User):
    try:
        r = requests.post(url="http://api:5000/user/" + API_KEY, data=user.json())
    except AttributeError:
        print(r.json())


async def add_message(message: models.Message):
    try:
        r = requests.post(url="http://api:5000/message/" + API_KEY, data=message.json())
    except AttributeError:
        print(r.json())


async def delete_message(message_id: int):
    """
    Called by on_message_delete, on_bulk_message_delete, on_raw_bulk_message_delete, on_raw_message_delete
    """
    _ = requests.delete(url=f"http://api:5000/message/?message_id={message_id}" + "&" + API_KEY[1:])


async def add_attachment(a: models.Attachment):
    try:
        _ = requests.post(url="http://api:5000/attachment/" + API_KEY, data=a.json())
    except AttributeError:
        print(a)


async def delete_attachments(message_id: int):
    _ = requests.delete(url=f"http://api:5000/attachment/?message_id={message_id}" + "&" + API_KEY[1:])


async def add_reaction(reaction: models.Reaction):
    try:
        _ = requests.post(url="http://api:5000/reaction/" + API_KEY, data=reaction.json())
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
    _ = requests.delete(url=f"http://api:5000/reaction/?message_id={message_id}" + "&" + API_KEY[1:])


async def delete_channel(channel_id: int):
    _ = requests.delete(url=f"http://api:5000/channel/?channel_id={channel_id}" + "&" + API_KEY[1:])


def delete_server(server_id):
    _ = requests.delete(url=f"http://api:5000/server/?server_id={server_id}" + "&" + API_KEY[1:])
