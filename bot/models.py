"""
2020-12-06
Migrating from RAW SQL PARTY to pydantic models.
Primary goal is to use separated API and send data to it, decoupling this mess from SQLite
and other hardcoded spaghetti.
"""

import datetime
from typing import Any, List, Optional

from pydantic import BaseModel


class User(BaseModel):
    # TODO should iterate all users on boot and add new on events! on_join
    id: int
    username: str
    # FIXME Problem if bot runs in multiple servers with same users, race condition...
    #  use nick, since it is global!
    display_name: str
    is_bot: bool


class Server(BaseModel):
    id: int
    name: str
    owner_id: int
    is_deleted: bool


class Channel(BaseModel):
    id: int
    server_id: int
    name: str
    position: int  # Will help to sort channels in graphs, to help change layout :^)
    is_deleted: bool


class Reaction(BaseModel):
    message_id: int
    reaction_id: str
    reaction_hash: int
    reacted_id: int
    is_deleted: bool


# noinspection PyRedeclaration
class Message(BaseModel):
    """
    More fields can be found: https://discordpy.readthedocs.io/en/latest/api.html#message
    """

    message_id: int
    author_id: int
    channel_id: int
    server_id: int
    date_utc: datetime.datetime
    date_last_edited_utc: Optional[datetime.datetime]
    length: int
    # content: str # TODO store content for API extraction? use message.clean_content
    is_pinned: bool
    is_everyone_mention: bool
    is_deleted: bool


class Attachment(BaseModel):
    message_id: int
    url: str
