from typing import Optional

from fastapi import FastAPI
from pymongo import MongoClient

from api import models

api = FastAPI()
client = MongoClient("mongodb://admin:password@mongo:27017")
db = client["lil_analytics"]
col_messages = db["messages"]


@api.get("/")
def read_root():
    return {"Hello": "World"}


@api.get("/message/all")
async def get_message():
    messages = []
    for message in col_messages.find():
        messages.append(models.Message(**message))
    return {"messages": messages}


@api.post("/message/{message_id}")
async def create_message(message: models.Message):
    # TODO look up by message_id and insert if doesnt exist! otherwise upsert!
    if hasattr(message, 'id'):
        delattr(message, 'id')
    ret = col_messages.insert_one(message.dict(by_alias=True))
    message.id = ret.inserted_id
    return {'message': message}


@api.delete("/message/{message_id}")
async def delete_message(message_id: int):
    ret = col_messages.find_one({"message_id": message_id})
    return {"message": ret}
