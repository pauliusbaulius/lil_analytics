from sqlalchemy.orm import Session
import datetime

from api import models, schemas


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict(), db_upserted=datetime.datetime.utcnow())
    db.merge(db_message)
    db.commit()
    #db.refresh(db_message)
    return db_message


def delete_message_by_id(db, message_id):
    db_message = db.query(models.Message).filter(models.Message.message_id == message_id).first()
    db_message.is_deleted = True
    db.commit()
    return db_message


def get_message_by_id(db: Session, message_id: int):
    return db.query(models.Message).filter(models.Message.message_id == message_id).first()

def get_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Message).limit(limit).all()

def create_attachment(db: Session, attachment: schemas.AttachmentCreate):
    db_attachment = models.Attachment(**attachment.dict())
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment

def get_attachment_by_url(db: Session, url: str):
    return db.query(models.Attachment).filter(models.Attachment.url == url).first()

def get_attachments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Attachment).limit(limit).all()

def create_server(db: Session, server: schemas.ServerCreate):
    db_server = models.Server(**server.dict())
    db.merge(db_server)
    db.commit()
    #db.refresh(db_server)
    return db_server

def get_server_by_id(db: Session, id: int):
    return db.query(models.Server).filter(models.Server.id == id).first()


def get_servers(db: Session):
    return db.query(models.Server).all()


def create_channel(db: Session, channel: schemas.ChannelCreate):
    db_channel = models.Channel(**channel.dict())
    db.merge(db_channel)
    db.commit()
    #db.refresh(db_channel)
    return db_channel


def get_channel_by_id(db: Session, id: int):
    return db.query(models.Channel).filter(models.Channel.id == id).first()


def get_channels(db: Session):
    return db.query(models.Channel).all()


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.merge(db_user)
    db.commit()
    #db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()


def get_users(db: Session):
    return db.query(models.User).all()


def create_reaction(db: Session, reaction: schemas.ReactionCreate):
    db_reaction = models.Reaction(**reaction.dict())
    db.merge(db_reaction)
    db.commit()
    return db_reaction


def get_reaction_by_ids(db: Session, message_id: int, reacted_id: int, reaction_id: str):
    return db.query(models.Reaction).filter(models.Reaction.message_id == message_id,
                                            models.Reaction.reacted_id == reacted_id,
                                            models.Reaction.reaction_id == reaction_id).first()


def get_reactions_by_message_id(db: Session, message_id: int):
    return db.query(models.Reaction).filter(models.Reaction.message_id == message_id).all()


def get_reactions(db: Session):
    return db.query(models.Reaction).all()

def get_reactions_by_channel(db: Session, channel_id: int):
    pass

def get_reactions_by_server(db: Session, server_id: int):
    pass

def delete_reaction_by_ids(db, message_id, reaction_id, reacted_id):
    db_reaction = db.query(models.Reaction).filter(models.Reaction.message_id == message_id,
                                                  models.Reaction.reacted_id == reacted_id,
                                                  models.Reaction.reaction_id == reaction_id).first()
    db_reaction.is_deleted = True
    db.commit()
    return db_reaction
# def get_user_by_email(db: Session, email: str):
#     return db.query(models.User).filter(models.User.email == email).first()
#
#
# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()
#
#
#
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
