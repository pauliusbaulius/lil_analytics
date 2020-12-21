import datetime
from typing import List, Optional

from pydantic import BaseModel


class ServerBase(BaseModel):
    id: int
    name: str
    owner_id: int
    is_deleted: bool


class ServerCreate(ServerBase):
    pass


class Server(ServerCreate):
    class Config:
        orm_mode = True


class ChannelBase(BaseModel):
    id: int
    server_id: int
    name: str
    position: int
    is_deleted: bool


class ChannelCreate(ChannelBase):
    pass


class Channel(ChannelCreate):
    class Config:
        orm_mode = True


class UserBase(BaseModel):
    id: int
    username: str
    display_name: str
    is_bot: bool


class UserCreate(UserBase):
    pass


class User(UserCreate):
    # messages = Optional[List[Message]]
    # mentioned_in = Optional[List[Message]]
    class Config:
        orm_mode = True


class AttachmentBase(BaseModel):
    message_id: int
    url: str


class AttachmentCreate(AttachmentBase):
    pass


class Attachment(AttachmentCreate):
    class Config:
        orm_mode = True


class ReactionBase(BaseModel):
    message_id: int
    reacted_id: int
    reaction_id: str
    reaction_hash: int
    is_deleted: bool


class ReactionCreate(ReactionBase):
    pass


class Reaction(ReactionCreate):
    class Config:
        orm_mode = True


class MessageCreate(BaseModel):
    message_id: int
    author_id: int
    channel_id: int
    server_id: int

    date_utc: datetime.datetime
    date_last_edited_utc: Optional[datetime.datetime]
    length: int
    is_pinned: bool
    is_everyone_mention: bool
    is_deleted: bool


class MessageBase(MessageCreate):
    db_upserted: datetime.datetime
    pass


class Message(MessageBase):
    attachments: Optional[List[Attachment]]
    author: User = None
    channel: Channel = None
    server: Server = None
    reactions: Optional[List[Reaction]]

    db_upserted: datetime.datetime

    class Config:
        orm_mode = True
