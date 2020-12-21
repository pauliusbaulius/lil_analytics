from typing import List

from fastapi import Depends, FastAPI, HTTPException

from sqlalchemy.orm import Session

from api import crud, models, schemas
from api.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
    SERVER
"""


@app.post("/server/", response_model=schemas.Server)
def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db)):
    return crud.create_server(db=db, server=server)


@app.delete("/server/", response_model=schemas.Server)
def delete_server(server_id: int, db: Session = Depends(get_db)):
    return crud.delete_server(server_id=server_id, db=db)


@app.get("/server/channels/{server_id}", response_model=List[schemas.Channel])
def get_server_channels(server_id: int, db: Session = Depends(get_db)):
    return crud.get_server_channels(server_id=server_id, db=db)


"""
    CHANNEL
"""


@app.post("/channel/", response_model=schemas.Channel)
def create_channel(channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    return crud.create_channel(db=db, channel=channel)


@app.delete("/channel/", response_model=schemas.Channel)
def delete_channel(channel_id: int, db: Session = Depends(get_db)):
    return crud.delete_channel(channel_id=channel_id, db=db)

"""
    USER
"""
@app.post("/user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)

@app.get("/user/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_by_id(user_id=user_id, db=db)

"""
    MESSAGE
"""


@app.post("/message/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)


@app.delete("/message/", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    crud.delete_attachments_by_id(message_id=message_id, db=db)
    crud.delete_reactions(message_id=message_id, db=db)
    return crud.delete_message_by_id(db, message_id=message_id)


@app.get("/messages/", response_model=List[schemas.Message])
def get_messages(
                 server_id: int = None,
                 channel_id: int = None,
                 user_id: int = None,
                 db: Session = Depends(get_db), limit: int = 100):
    return crud.get_messages(server_id=server_id,
                             channel_id=channel_id,
                             user_id=user_id,
                             db=db, limit=limit)


@app.get("/message/{message_id}", response_model=schemas.Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    return crud.get_message_by_id(db, message_id=message_id)


"""
    ATTACHMENT
"""


@app.post("/attachment/", response_model=schemas.Attachment)
def create_attachment(
    attachment: schemas.AttachmentCreate, db: Session = Depends(get_db)
):
    db_message = crud.get_attachment_by_url(db, url=attachment.url)
    if db_message:
        raise HTTPException(
            status_code=400, detail=f"Attachment [{attachment.url}] already exists!"
        )
    return crud.create_attachment(db=db, attachment=attachment)


@app.delete("/attachment/", response_model=List[schemas.Attachment])
def delete_attachments(message_id: int, db: Session = Depends(get_db)):
    return crud.delete_attachments_by_id(db, message_id=message_id)


@app.get("/attachments/{message_id}", response_model=List[schemas.Attachment])
def get_attachments_by_id(message_id: int, db: Session = Depends(get_db)):
    return crud.get_attachments_by_message_id(db, message_id=message_id)


# @app.get("/attachments/", response_model=List[schemas.Attachment])
# def get_attachments(server_id: int, channel_id:int, limit: int = 100, db: Session = Depends(get_db)):
#     return crud.get_attachments(server_id=server_id, channel_id=channel_id, limit=limit, db=db)

"""
    REACTION
"""


@app.post("/reaction/", response_model=schemas.Reaction)
def create_reaction(reaction: schemas.ReactionCreate, db: Session = Depends(get_db)):
    return crud.create_reaction(db=db, reaction=reaction)


# TODO figure out this thing and have RESTful api, not delete via is_deleted=1 using app.post...
# @app.delete("/reaction/", response_model=schemas.Reaction)
# def delete_reaction(message_id: int = Path(...),
#                     reaction_id: int = Path(...),
#                     reacted_id: int = Path(...),
#                     db: Session = Depends(get_db)):
#     print(message_id, reacted_id, reaction_id)
#     return crud.delete_reaction_by_ids(db, message_id=message_id, reaction_id=reaction_id, reacted_id=reacted_id)

@app.get("/reactions/{message_id}", response_model=List[schemas.Reaction])
def get_reactions_by_id(message_id: int, db: Session = Depends(get_db)):
    return crud.get_reactions_by_message_id(message_id=message_id, db=db)


# @app.get("/reactions/", response_model=List[schemas.Reaction])
# def get_reactions(server_id: int, channel_id: int, reacted_id:int, db: Session = Depends(get_db)):
#     return crud.get_reactions(server_id=server_id, channel_id=channel_id, reacted_id=reacted_id, db=db)