import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from api import models, schemas
from api.database import SessionLocal

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
        db_channel.is_deleted = True
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


"""
    DATA VISUALIZATION QUERIES HAPPEN HERE
"""


def get_server_channel_messages(server_id: int, db: Session, after: str = None):
    """
    Queries total messages for each channel for given server_id.
    Returns dictionary of labels and data for chart.js.
    Can give a date to filter from a date in history.

    How:
        1. Get all channels for matching server_id from table "channel"
        2. Count total messages for each channel_id!
        3. Channel names are labels, data is amount of messages per channel.
    """
    # TODO calculate average, mean and append to return json
    labels = []
    data = []

    query = db.query(models.Channel).filter_by(server_id=server_id, is_deleted=0).all()
    for channel in query:
        labels.append(channel.name)
        # Count amount of messages.
        data.append(db.query(models.Message).filter_by(channel_id=channel.id, is_deleted=0).count())

    return {"labels": labels, "data": data}


def get_server_total_messages(server_id: int, db: Session, after: str = None):
    messages = db.query(models.Message).filter_by(server_id=server_id, is_deleted=0).count()
    deleted = db.query(models.Message).filter_by(server_id=server_id, is_deleted=1).count()
    return {"server_id": server_id, "total_messages": messages, "total_deleted": deleted}


def get_server_stats(server_id: int, db: Session):
    # TODO add more fields to server like url, voice channels, whatever else
    server = db.query(models.Server).filter_by(id=server_id).first()
    owner = db.query(models.User).filter_by(id=server.owner_id).first()
    return {"server_id": server_id, "name": server.name, "owner_name": owner.username}


def get_server_message_growth(server_id: int, db: Session, days: int = 7):
    # TODO call get_Server_total_messages with appropriate after dates!
    # so for 2 days -> today and today -1
    # for 7 days -> today t-1 t-2 t-3 t-4 t-5 t-6
    # if -1, query all and append to other results, so you get growth with past messages!
    # append -1 to the oldest, and then accumulate over rest! so t-5 = t-6 and t-6 is t-6+-1
    pass


"""
    FROM OLD VERSION
"""


def get_messages_per_day(guild_id: int, days: int, channel_id=None, user_id: int = None) -> list:
    """Returns list of tuples of total messages for given amount of days. If channel id is given, returns total
    messages per day for that channel.
    If days are 0 or less, stats for all days will be returned!
    If you want to see total messages per day in all channels for last 7 days or you want to see total messages in a
    channel for past 14 days. There is no limit how long back you want to go. If you give 99999 it will return all
    counts for all days that are logged in the database.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    if days <= 0:
        days = -1

    sql = f"""SELECT DATE(date), COUNT(DATE(date)) 
              FROM messages
              WHERE {where} AND deleted == 0
              GROUP BY DATE(date) 
              ORDER BY DATE(date) DESC
              LIMIT {days}"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_messages_growth_days(guild_id: int, days: int, channel_id=None, user_id: int = None) -> list:
    """Returns accumulated list of message growth for server, channel, user or user in channel per day.
    Uses the function above to get message counts per day and then accumulates them. So day 2 will have count for day 2
    and count of day 1. Day 3 will have day 2 + day 1...
    """
    data = get_messages_per_day(guild_id=guild_id, user_id=user_id, channel_id=channel_id, days=days)

    new_data = []
    sum_ = 0
    for x in reversed(data):
        sum_ += x[1]
        new_data.append((x[0], sum_))

    return list(new_data)


def get_messages_per_month(guild_id: int, months: int, channel_id=None, user_id: int = None) -> list:
    """Returns messages written in a month in a server, channel, by user or by user in a specific channel.
    If months are -1, stats for all month will be returned.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    if months <= 0:
        months = -1

    sql = f"""SELECT strftime('%Y-%m', date), COUNT(strftime('%Y-%m', date)) 
              FROM messages
              WHERE {where} AND deleted == 0
              GROUP BY 1
              ORDER BY 1 DESC
              LIMIT {months}"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_messages_growth_months(guild_id: int, months: int, channel_id=None, user_id: int = None) -> list:
    """Returns a list of accumulative values for server/channel/user/user in a channel for a given amount of months.
    Amount of months can be specified. -1 returns all months since creation of the server (if messages are indexed).
    """
    data = get_messages_per_month(guild_id=guild_id, months=months, channel_id=channel_id, user_id=user_id)

    new_data = []
    sum_ = 0
    for x in reversed(data):
        sum_ += x[1]
        new_data.append((x[0], sum_))

    return list(new_data)


def get_messages_by_hour(guild_id: int, user_id: int = None, channel_id: int = None) -> list:
    """Returns total messages per hour for all server, channel or user.
    If both channel id and user id are given, returns data for user in that channel.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    sql = f"""SELECT strftime('%H', date), COUNT(strftime('%H', date)) 
              FROM messages
              WHERE {where} AND deleted == 0
              GROUP BY 1
              ORDER BY 1 ASC"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_messages_by_hour_days(guild_id: int, days: int, user_id: int = None, channel_id: int = None) -> list:
    """Returns total messages per hour for all server, channel or user within a range in days.
    If both channel id and user id are given, returns data for user in that channel.

        Parameters:

        Returns:

    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""

    sql = f"""SELECT strftime('%H', date) AS hour
              ,COUNT(strftime('%H', date))
              FROM (
                  SELECT *
                  FROM messages
                  WHERE {date} {where} AND deleted == 0
                  ORDER BY DATE DESC
                    )
              GROUP BY hour
              ORDER BY hour ASC"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_user_most_active(guild_id: int, amount: int, channel_id: int = None, days: int = -1) -> list:
    """Returns given amount of users by their messages in the server or channel in descending order.
    Can limit amount of returned users. Passing amount as -1 will return all users.
    """

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = (
        f"(SELECT * FROM messages WHERE date >= DATETIME ('now', '-{days + 1} days')) messages"
        if days >= 1
        else "messages"
    )

    if channel_id:
        sql = f"""SELECT count(messages.id), author_name 
                  FROM {date}
                  WHERE server_id == {guild_id} AND channel_id = {channel_id} AND deleted == 0
                  GROUP BY author_name 
                  ORDER BY count(id) DESC
                  LIMIT {amount}"""
    else:
        sql = f"""SELECT count(messages.id), author_name 
                  FROM {date}
                  WHERE server_id == {guild_id} AND deleted == 0
                  GROUP BY author_name 
                  ORDER BY count(id) DESC
                  LIMIT {amount}"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_reactions_today(guild_id: int):
    sql = f"""select count(), reaction_id
                  from message_reactions join messages on message_reactions.id == messages.id
                  where server_id == {guild_id} AND messages.deleted == 0 AND DATE(messages.date) == DATE('now')
                  group by reaction_id
                  order by count() desc"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_reaction_given_counts(guild_id: int, user_id: int = None, channel_id: int = None) -> list:
    """Returns a list of tuples for each reaction given by a user. If channel id is given, returns given reactions
    for that channel only. Otherwise reactions for all messages in the server.
    If you want to get received reactions, use the method above.
    """
    if channel_id and user_id:
        where = f"server_id == {guild_id} AND channel_id == {channel_id} AND reacted_id == {user_id}"
    elif user_id:
        where = f"server_id == {guild_id} AND reacted_id == {user_id}"
    elif channel_id:
        where = f"server_id == {guild_id} AND channel_id == {channel_id}"
    else:
        where = f"server_id == {guild_id}"

    sql = f"""select count(), reaction_id
              from message_reactions join messages on message_reactions.id == messages.id
              where {where} AND messages.deleted == 0
              group by reaction_id
              order by count() desc"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


def get_messages_by_weekday_days(guild_id: int, days: int, user_id: int = None, channel_id: int = None) -> list:
    """Returns messages by weekday for server, channel, user or user in a channel. 0 is Sunday, 6 is Monday.
    If parameter days is 0 or less, query is treated as query for all existing messages.
    """

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""

    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    sql = f"""SELECT strftime('%w', date) AS day, COUNT(strftime('%w', date))
              FROM (
                SELECT *
                FROM messages
                WHERE {date} {where} AND deleted == 0
                ORDER BY DATE DESC
               )
               GROUP BY day
               ORDER BY day ASC
              """

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()

    days = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

    # Convert integer to weekday and return list shifted by one day, so monday is first, saturday is last.
    data = [(days[int(x[0])], x[1]) for x in data]
    return data[1:] + [data[0]]


def get_message_hour_weekday_heatmap(guild_id: int, channel_id: int = None, user_id: int = None):
    """Returns a list of tuples (hour, weekday, amount of messages) for each hour and weekday of the week as a map.
    Considers all messages in the database for this query. Not limited by day.
    Used to build a heat map of message distribution by hour/weekday.
    Arguments:
        guild_id: Integer id of the server
        channel_id: Integer id of the channel
        user_id: Integer id of the user
    Returns:
        (hour 00-23, weekday Monday-Sunday, amount of messages in that hour/weekday)
    """
    where = get_conditional_where(guild_id=guild_id, channel_id=channel_id, user_id=user_id)

    sql = f"""SELECT strftime('%H', date) AS hour, 
                     strftime('%w', date) AS weekday, 
                     COUNT(strftime('%H', date)) as amount
              FROM messages
              WHERE {where} AND deleted == 0
              GROUP BY hour, weekday"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()

    days = {0: "Sunday", 1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

    # Convert integer to weekday and return list shifted by one day, so monday is first, saturday is last.
    data = [(x[0], days[int(x[1])], x[2]) for x in data]
    # Resort data so monday is the first day of the week, instead of sunday.
    return sorted(data, key=lambda x: sort_weekday(x[1]))
