from typing import List

from fastapi import Depends, FastAPI, HTTPException, Path
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


@app.post("/message/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message)


@app.delete("/message/{message_id}", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db)):
    return crud.delete_message_by_id(db, message_id=message_id)


@app.get("/message/all", response_model=List[schemas.Message])
def get_messages(db: Session = Depends(get_db), limit: int = 100):
    return crud.get_messages(db, limit=limit)


@app.get("/message/{message_id}", response_model=schemas.Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    return crud.get_message_by_id(db, message_id=message_id)


@app.post("/attachment/", response_model=schemas.Attachment)
def create_attachment(attachment: schemas.AttachmentCreate, db: Session = Depends(get_db)):
    db_message = crud.get_attachment_by_url(db, url=attachment.url)
    if db_message:
        raise HTTPException(status_code=400, detail=f"Attachment [{attachment.url}] already exists!")
    return crud.create_attachment(db=db, attachment=attachment)


@app.post("/server/", response_model=schemas.Server)
def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db)):
    return crud.create_server(db=db, server=server)


@app.post("/channel/", response_model=schemas.Channel)
def create_channel(channel: schemas.ChannelCreate, db: Session = Depends(get_db)):
    return crud.create_channel(db=db, channel=channel)


@app.post("/user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


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
