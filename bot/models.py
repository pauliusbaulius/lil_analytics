"""
2020-12-06
Migrating from RAW SQL PARTY to pydantic models.
Primary goal is to use separated API and send data to it, decoupling this mess from SQLite
and other hardcoded spaghetti.
"""

import datetime
from typing import List, Optional, Any

from pydantic import BaseModel


class Message(BaseModel):
    # Blank model for Python' one-pass-evaluation.
    pass


class User(BaseModel):
    user_id: int
    name: str
    # FIXME Problem if bot runs in multiple servers with same users, race condition...
    #  use nick, since it is global!
    display_name: str


class Server(BaseModel):
    server_id: int
    name: str
    is_deleted: bool
    owner_id: int


class Channel(BaseModel):
    channel_id: int
    server_id: int
    name: str
    position: int  # Will help to sort channels in graphs, to help change layout :^)
    is_deleted: bool


class Reaction(BaseModel):
    message_id: Message
    reaction_id: str
    reaction_hash: int


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
    attachments: Optional[List[str]]
    is_bot: bool
    is_pinned: bool
    is_everyone_mention: bool
    is_deleted: bool

    mentions: Optional[List[int]]
    channel_mentions: Optional[List[int]]
    # TODO RoleMention if needed. Do not see point in having it now, since nobody cares yet.
    # role_mentions: Optional[List[int]]


