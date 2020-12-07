import datetime

from pydantic import BaseModel, Field
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional, List

client = MongoClient()
db = client.test


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class Message(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id')
    message_id: int
    author_id: int
    channel_id: int
    server_id: int
    date_utc: datetime.datetime
    date_last_edited_utc: Optional[datetime.datetime]
    length: int
    attachments: Optional[List[str]]
    is_pinned: bool
    is_everyone_mention: bool
    is_deleted: bool
    mentions: Optional[List[int]]
    channel_mentions: Optional[List[int]]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }