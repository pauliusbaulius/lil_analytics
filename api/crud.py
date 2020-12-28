import datetime
import statistics
from typing import Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from api import models, schemas


def get_conditional_where(server_id: int, channel_id: int = None, user_id: int = None) -> str:
    """
    Builds WHERE clause parameters for SQL query given guild, user, channel id combinations.
    If you want WHERE channel_id == ?, pass guild_id
    If you want WHERE channel_id == ? AND user_id == ?, pass guild_id and user_id
        Parameters:
            server_id: Integer id of the server
            channel_id: Integer id of the channel
            user_id: Integer id of the user
        Returns:
            SQL WHERE parameters matching given ids without WHERE keyword.
    """
    if channel_id and user_id:
        where = f"server_id == {server_id} AND channel_id == {channel_id} AND author_id == {user_id}"
    elif user_id:
        where = f"server_id == {server_id} AND author_id == {user_id}"
    elif channel_id:
        where = f"server_id == {server_id} AND channel_id == {channel_id}"
    else:
        where = f"server_id == {server_id}"
    return where


def check_existence(db: Session, server_id: int = None, channel_id: int = None, user_id: int = None) -> int:
    """
    Checks whether given server/channel/user id exist in the database.
    If they do not, HTTP error is raised!
        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            db: Database session.
        Returns:
            Boolean whether given parameters exist or not.
    """
    server = get_server_by_id(id=server_id, db=db)
    if not server:
        raise HTTPException(status_code=404, detail=f"server with id: {server_id} does not exist.")
    if channel_id:
        channel = get_channel_by_id(db=db, id=channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail=f"channel with id: {channel_id} does not exist.")
    if user_id:
        user = get_user_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"user with id: {user_id} does not exist.")
    return True


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
    """
    db_server = db.query(models.Server).filter(models.Server.id == server_id).first()
    try:
        db_server.is_delete = True
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
        db_channel.is_deleted = True
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


"""
    FROM OLD VERSION
"""


def get_messages_amount_days(days: int, db: Session, server_id: int, channel_id: int = None, user_id: int = None):
    if days > 90 or days < 0:
        days = 90

    # 0 should be treated as today!
    if days == 0:
        days = 1

    statement = text(
        f"""SELECT DATE(date_utc), COUNT(DATE(date_utc)) 
            FROM message
            WHERE {get_conditional_where(server_id, channel_id, user_id)} AND is_deleted == 0
            GROUP BY DATE(date_utc) 
            ORDER BY DATE(date_utc) DESC
            LIMIT {days + 1}"""
    )
    res = list(db.execute(statement))

    labels = []
    data = []

    # Query returns messages for days that messages exist, so you will get gaps like
    # ('2020-12-30', 300), ('2020-12-20', 100). This leaves 10 days gap and gets another 8 days
    # from the past. We want to fill those gaps with 0 messages as ('2020-12-29', 0)...
    # This loop will iterate list of results, calculate time delta and fill gaps with new dates and 0 messages!
    # Return is then limited to passed amount of days, since filled list may contain a lot more.
    for i in range(len(res) - 1):
        x = datetime.date.fromisoformat(res[i][0])
        y = datetime.date.fromisoformat(res[i + 1][0])
        delta = x - y
        if delta.days > 1:
            for i in range(delta.days):
                new_date = x - datetime.timedelta(days=i)
                labels.append(str(new_date))
                data.append(0)
        else:
            labels.append(res[i][0])
            data.append(res[i][1])
    labels = labels[:days]
    data = data[:days]

    average = sum(data) / len(data)
    median = statistics.median(data)

    # Reverse data to get from oldest to newest date.
    return {"labels": labels[::-1], "data": data[::-1], "average": average, "median": median}


def get_messages_growth_days(
    db: Session, server_id: int, days: int, channel_id: int = None, user_id: int = None
) -> Dict:
    d = get_messages_amount_days(server_id=server_id, user_id=user_id, channel_id=channel_id, days=days, db=db)
    data, _sum = [], 0
    # Accumulate and replace old data with accumulated data.
    for x in zip(d["labels"], d["data"]):
        _sum += x[1]
        data.append(_sum)
    return {"labels": d["labels"], "data": data}


def get_messages_per_month(db: Session, server_id: int, months: int, channel_id=None, user_id: int = None) -> Dict:
    """
    Returns messages written in a month in a server, channel, by user or by user in a specific channel.
    If months are -1, stats for all month will be returned.
    """
    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    if months <= 0:
        months = -1

    statement = text(
        f"""SELECT strftime('%Y-%m', date_utc), COUNT(strftime('%Y-%m', date_utc)) 
              FROM message
              WHERE {where} AND is_deleted == 0
              GROUP BY 1
              ORDER BY 1 DESC
              LIMIT {months}"""
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[0])
        data.append(x[1])

    return {"labels": labels[::-1], "data": data[::-1]}


def get_messages_growth_months(db: Session, server_id: int, months: int, channel_id=None, user_id: int = None) -> Dict:
    d = get_messages_per_month(server_id=server_id, months=months, channel_id=channel_id, user_id=user_id, db=db)
    print(d)
    data, _sum = [], 0
    for x in zip(d["labels"], d["data"]):
        _sum += x[1]
        data.append(_sum)
    return {"labels": d["labels"], "data": data}


def get_messages_by_hour(db: Session, server_id: int, user_id: int = None, channel_id: int = None) -> Dict:
    """Returns total messages per hour for all server, channel or user.
    If both channel id and user id are given, returns data for user in that channel.
    """
    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    statement = text(
        f"""SELECT strftime('%H', date_utc), COUNT(strftime('%H', date_utc)) 
              FROM message
              WHERE {where} AND is_deleted == 0
              GROUP BY 1
              ORDER BY 1 ASC"""
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[0])
        data.append(x[1])

    return {"labels": labels, "data": data}


@DeprecationWarning
def get_messages_by_hour_days(
    db: Session, server_id: int, days: int, user_id: int = None, channel_id: int = None
) -> Dict:
    """Returns total messages per hour for all server, channel or user within a range in days.
    If both channel id and user id are given, returns data for user in that channel.

        Parameters:

        Returns:

    """
    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""

    statement = text(
        f"""SELECT strftime('%H', date_utc) AS hour
              ,COUNT(strftime('%H', date_utc))
              FROM (
                  SELECT *
                  FROM message
                  WHERE {date} {where} AND is_deleted == 0
                  ORDER BY DATE DESC
                    )
              GROUP BY hour
              ORDER BY hour ASC"""
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[0])
        data.append(x[1])

    return {"labels": labels, "data": data}


def get_user_most_active(db: Session, server_id: int, amount: int, channel_id: int = None, days: int = -1) -> list:
    """Returns given amount of users by their messages in the server or channel in descending order.
    Can limit amount of returned users. Passing amount as -1 will return all users.
    """
    if days == 0:
        days = 1

    if days < 0:
        days = -1

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = (
        f"(SELECT * FROM message WHERE date_utc >= DATETIME ('now', '-{days + 1} days')) message"
        if days >= 1
        else "message"
    )

    if channel_id:
        statement = text(
            f"""SELECT count(message_id), username
                  FROM {date} JOIN user ON message.author_id == user.id
                  WHERE server_id == {server_id} AND channel_id = {channel_id} AND is_deleted == 0
                  GROUP BY author_id 
                  ORDER BY count(message_id) DESC
                  LIMIT {amount}"""
        )
    else:
        statement = text(
            f"""SELECT count(message_id), username
                      FROM {date} JOIN user ON message.author_id == user.id
                      WHERE server_id == {server_id} AND is_deleted == 0
                      GROUP BY author_id 
                      ORDER BY count(message_id) DESC
                      LIMIT {amount}"""
        )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[1])
        data.append(x[0])

    return {"labels": labels, "data": data}


def get_reactions_today(db: Session, server_id: int):
    statement = text(
        f"""SELECT COUNT(), reaction_id
                  FROM reaction JOIN message ON reaction.message_id == message.message_id
                  WHERE server_id == {server_id} AND message.is_deleted == 0 AND DATE(message.date_utc) == DATE('now')
                  GROUP BY reaction_id
                  ORDER BY COUNT() DESC"""
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[1])
        data.append(x[0])

    return {"labels": labels, "data": data}


def get_reaction_given_counts(db: Session, server_id: int, user_id: int = None, channel_id: int = None) -> list:
    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    statement = text(
        f"""select count(), reaction_id
            FROM reaction JOIN message ON reaction.message_id == message.message_id
            where {where} AND message.is_deleted == 0
            group by reaction_id
            order by count() desc"""
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[1])
        data.append(x[0])

    return {"labels": labels, "data": data}


def get_messages_by_weekday(
    db: Session, server_id: int, days: int, user_id: int = None, channel_id: int = None
) -> list:
    if days < 0:
        days = -1

    if days == 1 or days == 0:
        days = 2

    # If user passes days as below 0, treat it as "query all days".
    date = f"date_utc >= DATETIME ('now', '-{days} days') AND" if days >= 1 else ""

    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    statement = text(
        f"""SELECT strftime('%w', date_utc) AS day, COUNT(strftime('%w', date_utc))
              FROM (
                SELECT *
                FROM message
                WHERE {date} {where} AND is_deleted == 0
                ORDER BY date_utc DESC
               )
               GROUP BY day
               ORDER BY day ASC
              """
    )

    res = list(db.execute(statement))

    labels = []
    data = []

    for x in res:
        labels.append(x[1])
        data.append(x[0])

    days = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

    # Convert integer to weekday and return list shifted by one day, so monday is first, saturday is last.
    data = [days[int(x)] for x in data]
    if len(data) > 1:
        return {"labels": labels[1:] + [labels[0]], "data": data[1:] + [data[0]]}  # Switch Sunday to back of the list!
    return {"labels": labels, "data": data}


def get_heatmap(db: Session, server_id: int, channel_id: int = None, user_id: int = None):
    where = get_conditional_where(server_id=server_id, user_id=user_id, channel_id=channel_id)

    statement = text(
        f"""SELECT strftime('%H', date_utc) AS hour, 
                     strftime('%w', date_utc) AS weekday, 
                     COUNT(strftime('%H', date_utc)) as amount
              FROM message
              WHERE {where} AND is_deleted == 0
              GROUP BY hour, weekday"""
    )

    res = list(db.execute(statement))

    days = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

    # TODO which one makes more sense!
    # data = []
    # for x in res:
    #     data.append((x[0]+ ":00", days[int(x[1])], x[2]))
    # return {"data": data}

    hour = []
    day = []
    messages = []
    for x in res:
        hour.append(x[0] + ":00")
        day.append(days[int(x[1])])
        messages.append(x[2])
    return {"hour": hour, "day": day, "messages": messages}

    # Resort data so monday is the first day of the week, instead of sunday.
    # return sorted(data, key=lambda x: sort_weekday(x[1]))
