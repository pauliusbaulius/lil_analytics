import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from api import models, schemas

"""
    SERVER
"""


def create_server(db: Session, server: schemas.ServerCreate):
    db_server = models.Server(**server.dict())
    db.merge(db_server)
    db.commit()
    # db.refresh(db_server)
    return db_server


def delete_server(server_id: int, db: Session) -> Optional[models.Server]:
    """
    Given server_id, sets is_deleted to True for the server and all messages related to the server.
    If
    """
    db_server = db.query(models.Server).filter(models.Server.id == server_id).first()
    try:
        db_server.is_delete = True
        # FIXME need to soft delete all messages of the server, but there must be a more efficient way than iteration!
        db_server_messages = db.query(models.Message).filter(models.Message.server_id == server_id).all()
        for message in db_server_messages:
            message.is_deleted = True
        db.commit()
        return db_server
    except ValueError:
        # TODO return error json?
        return None


def get_server_by_id(db: Session, id: int):
    return db.query(models.Server).filter(models.Server.id == id).first()


def get_servers(db: Session):
    return db.query(models.Server).all()


def get_server_channels(server_id, db):
    try:
        return db.query(models.Channel).filter(models.Channel.server_id == server_id).all()
    except ValueError:
        # TODO return error json?
        return None


"""
    CHANNEL
"""


def create_channel(db: Session, channel: schemas.ChannelCreate):
    db_channel = models.Channel(**channel.dict())
    db.merge(db_channel)
    db.commit()
    # db.refresh(db_channel)
    return db_channel


def delete_channel(channel_id: int, db: Session):
    db_channel = db.query(models.Channel).filter(models.Channel.id == channel_id).first()
    try:
        db_channel.is_delete = True
        # FIXME need to soft delete all messages of the channel, but there must be a more efficient way than iteration!
        db_server_messages = db.query(models.Message).filter(models.Message.channel_id == channel_id).all()
        for message in db_server_messages:
            message.is_deleted = True
        db.commit()
        return db_channel
    except AttributeError:
        # TODO return error json?
        return None


def get_channel_by_id(db: Session, id: int):
    return db.query(models.Channel).filter(models.Channel.id == id).first()


def get_channels(db: Session):
    return db.query(models.Channel).all()


"""
    USER
"""


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.merge(db_user)
    db.commit()
    # db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users(db: Session):
    return db.query(models.User).all()


"""
    MESSAGE
"""


def create_message(db: Session, message: schemas.MessageCreate):
    db_message = models.Message(**message.dict(), db_upserted=datetime.datetime.utcnow())
    db.merge(db_message)
    db.commit()
    # db.refresh(db_message)
    return db_message


def delete_message_by_id(db, message_id) -> Optional[models.Message]:
    """
    Deletes message given its id. If message does not exist, None is returned.
    Otherwise message is returned.
    """
    db_message = db.query(models.Message).filter(models.Message.message_id == message_id).first()
    try:
        db_message.is_deleted = True
        db.commit()
        return db_message
    except AttributeError:
        # TODO return error json?
        return None


def get_message_by_id(db: Session, message_id: int) -> Optional[models.Message]:
    return db.query(models.Message).filter(models.Message.message_id == message_id).first()


def get_messages(
    db: Session,
    channel_id: int = None,
    server_id: int = None,
    user_id: int = None,
    limit: int = 100,
) -> List[models.Message]:

    query = db.query(models.Message)
    if channel_id:
        print(channel_id)
        query = query.filter_by(channel_id=channel_id)
    if server_id:
        query = query.filter_by(server_id=server_id)
    if user_id:
        query = query.filter_by(author_id=user_id)
    return query.limit(limit).all()


"""
    ATTACHMENT
"""


def create_attachment(db: Session, attachment: schemas.AttachmentCreate) -> models.Attachment:
    db_attachment = models.Attachment(**attachment.dict())
    db.add(db_attachment)
    db.commit()
    db.refresh(db_attachment)
    return db_attachment


def delete_attachments_by_id(db, message_id):
    db_attachments = db.query(models.Attachment).filter(models.Attachment.message_id == message_id).all()
    for db_attachment in db_attachments:
        db_attachment.is_deleted = True
    db.commit()
    return db_attachments


def get_attachment_by_url(db: Session, url: str) -> Optional[models.Attachment]:
    return db.query(models.Attachment).filter(models.Attachment.url == url).first()


def get_attachments(
    db: Session,
    channel_id: int = None,
    server_id: int = None,
    limit: int = 100,
) -> List[models.Attachment]:
    # TODO join with messages? to be able to filter by channel/Server/user
    pass


def get_attachments_by_message_id(db: Session, message_id: int):
    return db.query(models.Attachment).filter(models.Attachment.message_id == message_id).all()


"""
    REACTION
"""


def create_reaction(db: Session, reaction: schemas.ReactionCreate):
    db_reaction = models.Reaction(**reaction.dict())
    db.merge(db_reaction)
    db.commit()
    return db_reaction


def get_reaction_by_ids(db: Session, message_id: int, reacted_id: int, reaction_id: str):
    return (
        db.query(models.Reaction)
        .filter(
            models.Reaction.message_id == message_id,
            models.Reaction.reacted_id == reacted_id,
            models.Reaction.reaction_id == reaction_id,
        )
        .first()
    )


def delete_reactions(message_id: int, db: Session) -> List[models.Reaction]:
    db_reactions = db.query(models.Reaction).filter(models.Reaction.message_id == message_id).all()
    for reaction in db_reactions:
        reaction.is_deleted = True
        db.commit()
    return db_reactions


def delete_reaction_by_ids(db, message_id, reaction_id, reacted_id):
    db_reaction = (
        db.query(models.Reaction)
        .filter(
            models.Reaction.message_id == message_id,
            models.Reaction.reacted_id == reacted_id,
            models.Reaction.reaction_id == reaction_id,
        )
        .first()
    )
    db_reaction.is_deleted = True
    db.commit()
    return db_reaction


def get_reactions_by_message_id(db: Session, message_id: int):
    return db.query(models.Reaction).filter(models.Reaction.message_id == message_id).all()


def get_reactions(
    db: Session,
    channel_id: int = None,
    server_id: int = None,
    reacted_id: int = None,
    reaction_id: str = None,
    limit: int = 100,
) -> List[models.Message]:
    # TODO join with messages to be able to query by server/channel/user!
    pass
