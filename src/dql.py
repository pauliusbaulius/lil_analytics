import datetime

from dateutil import parser

from src.decorators import timer
from src.utils import get_database, sort_weekday
import src.sqlite as sqlite


@timer
def get_messages_total(guild_id: int, channel_id: int = None, user_id: int = None) -> int:
    """Get total amount of specific user in a channel, of specific user in all server, all messages of one channel or
    whole server.

    Give server id to get amount of messages in server.
    Give channel id to get amount of messages in channel.
    Give user id to get amount of messages by the user in all channels.
    Give user id and channel id to get amount of messages by the user in that channel.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    sql = f"""SELECT count()
              FROM messages
              WHERE {where} AND deleted == 0"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchone()[0]

    return data


@timer
def get_messages_total_days(guild_id: int, days: int, channel_id: int = None, user_id: int = None) -> int:
    """Get message totals per day per guild, channel, by user or by user in a channel.
    If parameters days is 0 or lower, queries data for all indexed days.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""

    sql = f"""SELECT count()
              FROM (
                  SELECT *
                  FROM messages
                  WHERE {date} {where} AND deleted == 0
                  ORDER BY DATE DESC
                )"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchone()[0]
    return data


@timer
def get_messages_total_today(guild_id: int) -> int:
    # TODO
    sql = f"""SELECT count()
              FROM (
                  SELECT *
                  FROM messages
                  WHERE server_id == {guild_id} AND deleted == 0 AND DATE(messages.date) == DATE('now')
                  ORDER BY DATE DESC
              )"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchone()[0]
    return data


@timer
def get_messages_per_day(guild_id: int, days: int, channel_id=None, user_id: int = None) -> list:
    """Returns list of tuples of total messages for given amount of days. If channel id is given, returns total
    messages per day for that channel.

    If days are 0 or less, stats for all days will be returned!

    If you want to see total messages per day in all channels for last 7 days or you want to see total messages in a
    channel for past 14 days. There is no limit how long back you want to go. If you give 99999 it will return all
    counts for all days that are logged in the database.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    if days <= 0: days = -1

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


@timer
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


@timer
def get_messages_per_month(guild_id: int, months: int, channel_id=None, user_id: int = None) -> list:
    """Returns messages written in a month in a server, channel, by user or by user in a specific channel.
    If months are -1, stats for all month will be returned.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    if months <= 0: months = -1

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


@timer
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


@timer
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


@timer
def get_messages_by_hour_days(guild_id: int, days: int, user_id: int = None, channel_id: int = None) -> list:
    """Returns total messages per hour for all server, channel or user within a range in days.
    If both channel id and user id are given, returns data for user in that channel.
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


@timer
def get_messages_by_hour_today(guild_id: int) -> list:
    # TODO like above but only for this day date(messages.date)==date('now')
    sql = f"""SELECT strftime('%H', date) AS hour
              ,COUNT(strftime('%H', date))
              FROM (
                  SELECT *
                  FROM messages
                  WHERE server_id == {guild_id} AND deleted == 0 AND DATE(messages.date) == DATE('now')
                  ORDER BY DATE DESC
              )
              GROUP BY hour
              ORDER BY hour ASC"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


@timer
def get_user_message_date(guild_id: int, user_id: int, order: str = "DESC", tz: int = 0) -> str:
    """Get latest/first message date of user given user id and server id.
    Given order DESC, returns latest message, ASC returns first message.
    """
    c = sqlite.db_cursor
    c.execute(f"""select messages.date
                from messages
                WHERE author_id == {user_id} AND server_id == {guild_id}
                order by messages.date {order}
                limit 1""")

    date = parser.parse(c.fetchone()[0]) + datetime.timedelta(hours=tz)
    tz = f"UTC+{tz}" if tz >= 0 else f"UTC{tz}"
    return date.strftime(f"%Y-%m-%d %H:%M:%S {tz}")


@timer
def get_user_channel_activity(guild_id: int, user_id: int) -> list:
    """Gets total amount of messages per existing channel for given user id."""
    c = sqlite.db_cursor
    c.execute(f"""SELECT count(*) AS messages, channels.name
                  FROM messages INNER JOIN channels ON messages.channel_id == channels.id
                  WHERE messages.server_id == {guild_id} AND author_id == {user_id} AND messages.deleted == 0
                  GROUP BY messages.author_name, channels.name
                  ORDER BY count(*) DESC""")
    data = c.fetchall()
    return data


@timer
def get_user_most_active(guild_id: int, amount: int, channel_id: int = None, days: int = -1) -> list:
    """Returns given amount of users by their messages in the server or channel in descending order.
    Can limit amount of returned users. Passing amount as -1 will return all users.
    """

    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"(SELECT * FROM messages WHERE date >= DATETIME ('now', '-{days + 1} days')) messages" \
        if days >= 1 else "messages"

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


@timer
def get_user_most_active_today(guild_id: int, amount: int = -1):
    # TODO AND DATE(messages.date) == DATE('now')
    sql = f"""SELECT count(messages.id), author_name 
              FROM messages
              WHERE server_id == {guild_id} AND deleted == 0 AND DATE(messages.date) == DATE('now')
              GROUP BY author_name 
              ORDER BY count(id) DESC
              LIMIT {amount}"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


@timer
def get_channels_messages(guild_id: int, amount: int = -1, days: int = -1) -> list:
    """Returns a list of tuples for total messages in each channel of the server in descending order.
    Amount of servers can be specified with amount parameter. -1 returns all channels.
    """
    # If user passes days as 0 or below 0, treat it as "query all days".
    date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""

    c = sqlite.db_cursor
    c.execute(f"""SELECT count(*) AS messages, channels.name
                  FROM (
                      SELECT *
                      FROM messages INNER JOIN channels ON messages.channel_id == channels.id
                      WHERE {date} messages.server_id == {guild_id} AND messages.deleted == 0
                      ORDER BY DATE DESC
                        ) channels
                  GROUP BY channels.name
                  ORDER BY count(*) DESC
                  LIMIT {amount}""")
    data = c.fetchall()
    return data


@timer
def get_channels_messages_today(guild_id: int, amount: int = -1) -> list:
    #TODO
    c = sqlite.db_cursor
    c.execute(f"""SELECT count(*) AS messages, channels.name
                  FROM (
                      SELECT *
                      FROM messages INNER JOIN channels ON messages.channel_id == channels.id
                      WHERE messages.server_id == {guild_id} AND messages.deleted == 0 AND DATE(messages.date) == DATE('now')
                      ORDER BY DATE DESC
                        ) channels
                  GROUP BY channels.name
                  ORDER BY count(*) DESC
                  LIMIT {amount}""")
    data = c.fetchall()
    return data


@timer
def get_reaction_received_counts(guild_id: int, channel_id: int = None, user_id: int = None) -> list:
    """Returns a list of tuples for each reaction in the server and amount it has been used for
    whole server, a channel or a user.

    Counts occurrences of each reaction/emoji in all recorded reactions for a given server, channel or user.
    If you want amount for the whole server, pass a guild_id, for a channel - pass additional channel_id parameter.
    For user, pass user_id parameter. If you pass channel_id and user_id, it will return reactions for user in that
    channel.

    Giving user_id means getting reactions received by the user! Not reactions given!
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)

    sql = f"""select count(), reaction_id
              from message_reactions join messages on message_reactions.id == messages.id
              where {where} AND messages.deleted == 0
              group by reaction_id
              order by count() desc"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


@timer
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


@timer
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


@timer
def get_messages_length(guild_id, channel_id, user_id) -> list:
    """Get message lengths for all messages in guild, channel, by user or by user in a channel.

    Used to build histograms of message lengths. If you want to find out the distribution of message length
    in your server, of a user, of messages in a channel or messages of a particular user in a particular channel.
    """
    where = get_conditional_where(guild_id=guild_id, user_id=user_id, channel_id=channel_id)
    sql = f"""SELECT length
              FROM messages
              WHERE {where} AND length > 0 AND deleted == 0"""

    c = sqlite.db_cursor
    c.execute(sql)
    data = c.fetchall()
    return data


@timer
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

    days = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday"
    }

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

    days = {
        0: "Sunday",
        1: "Monday",
        2: "Tuesday",
        3: "Wednesday",
        4: "Thursday",
        5: "Friday",
        6: "Saturday"
    }

    # Convert integer to weekday and return list shifted by one day, so monday is first, saturday is last.
    data = [(x[0], days[int(x[1])], x[2]) for x in data]
    # Resort data so monday is the first day of the week, instead of sunday.
    return sorted(data, key=lambda x: sort_weekday(x[1]))


def get_conditional_where(guild_id: int, channel_id: int = None, user_id: int = None):
    """Builds WHERE clause parameters for SQL query given guild, user, channel id combinations.

    If you want WHERE channel_id == ?, pass guild_id
    If you want WHERE channel_id == ? AND user_id == ?, pass guild_id and user_id

    Arguments:
        guild_id: Integer id of the server
        channel_id: Integer id of the channel
        user_id: Integer id of the user

    Returns:
        SQL WHERE parameters matching given ids without WHERE keyword.
    """
    if channel_id and user_id:
        where = f"server_id == {guild_id} AND channel_id == {channel_id} AND author_id == {user_id}"
    elif user_id:
        where = f"server_id == {guild_id} AND author_id == {user_id}"
    elif channel_id:
        where = f"server_id == {guild_id} AND channel_id == {channel_id}"
    else:
        where = f"server_id == {guild_id}"
    return where