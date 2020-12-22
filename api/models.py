from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.database import Base


class Server(Base):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    owner_id = Column(Integer, ForeignKey("user.id"))
    is_deleted = Column(Boolean, default=False)


class Channel(Base):
    __tablename__ = "channel"
    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("server.id"))
    name = Column(String)
    position = Column(Integer)
    is_deleted = Column(Boolean, default=False)


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    display_name = Column(String)
    messages = relationship("Message", back_populates="author")
    is_bot = Column(Boolean)


class Message(Base):
    __tablename__ = "message"
    message_id = Column(Integer, primary_key=True, index=True)

    author_id = Column(Integer, ForeignKey("user.id"), index=True)
    channel_id = Column(Integer, ForeignKey("channel.id"), index=True)
    server_id = Column(Integer, ForeignKey("server.id"), index=True)

    date_utc = Column(DateTime, index=True)
    date_last_edited_utc = Column(DateTime, default=None)
    length = Column(Integer)
    is_pinned = Column(Boolean)
    is_everyone_mention = Column(Boolean)
    is_deleted = Column(Boolean, default=False)

    attachments = relationship("Attachment")
    author = relationship("User")
    channel = relationship("Channel")
    server = relationship("Server")
    reactions = relationship("Reaction")

    db_upserted = Column(DateTime)

    def _asdict(self):
        """
        Serialization logic for converting entities using flask's jsonify

        :return: An ordered dictionary
        :rtype: :class:`collections.OrderedDict`
        """


class Attachment(Base):
    __tablename__ = "attachment"
    message_id = Column(Integer, ForeignKey("message.message_id"), primary_key=True)
    url = Column(String, primary_key=True)
    is_deleted = Column(Boolean, default=False)


#    authors = relationship("Message", back_populates="attachments")


class Reaction(Base):
    __tablename__ = "reaction"
    message_id = Column(Integer, ForeignKey("message.message_id"), primary_key=True)
    reacted_id = Column(Integer, primary_key=True)
    reaction_id = Column(String, primary_key=True)
    reaction_hash = Column(Integer)
    is_deleted = Column(Boolean, default=False)
