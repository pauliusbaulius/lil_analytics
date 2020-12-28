import datetime
import os
import statistics
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKey, APIKeyHeader, APIKeyQuery
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles
from starlette.status import HTTP_403_FORBIDDEN

from api import crud, models, schemas
from api.crud import check_existence, get_conditional_where
from api.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
    AUTHENTICATION
"""

API_KEY = os.environ["FASTAPI_KEY"]
API_KEY_NAME = "api_key"
COOKIE_DOMAIN = os.environ["DOMAIN"]

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(
    api_key_query: str = Security(api_key_query),
    api_key_header: str = Security(api_key_header),
):

    if api_key_query == API_KEY:
        return api_key_query
    elif api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Unauthorized access! Access key is required!")


@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie(API_KEY_NAME, domain=COOKIE_DOMAIN)
    return response


@app.get("/test")
async def get_open_api_endpoint():
    return {"Hello": "World!"}


"""
    INDEX-DASHBOARD
"""


@app.get("/", response_class=HTMLResponse)
def index(request: Request, db: Session = Depends(get_db)):
    context = {"request": request, "timestamp": datetime.datetime.utcnow(), "servers": crud.get_servers(db=db)}
    return templates.TemplateResponse("index.html", context)


@app.get("/dashboard/{server_id}", response_class=HTMLResponse)
def dashboard(request: Request, server_id: int, db: Session = Depends(get_db)):
    context = {"request": request, "server_id": server_id}
    return templates.TemplateResponse("dashboard.html", context)


"""
    SERVER
"""


@app.post("/server/", response_model=schemas.Server)
def create_server(server: schemas.ServerCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return crud.create_server(db=db, server=server)


@app.delete("/server/", response_model=schemas.Server)
def delete_server(server_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return crud.delete_server(server_id=server_id, db=db)


@app.get("/server/channels/{server_id}", response_model=List[schemas.Channel])
def get_server_channels(server_id: int, db: Session = Depends(get_db)):
    return crud.get_server_channels(server_id=server_id, db=db)


"""
    CHANNEL
"""


@app.post("/channel/", response_model=schemas.Channel)
def create_channel(
    channel: schemas.ChannelCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)
):
    return crud.create_channel(db=db, channel=channel)


@app.delete("/channel/", response_model=schemas.Channel)
def delete_channel(channel_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return crud.delete_channel(channel_id=channel_id, db=db)


"""
    USER
"""


@app.post("/user/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return crud.create_user(db=db, user=user)


@app.get("/user/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_by_id(user_id=user_id, db=db)


"""
    MESSAGE
"""


@app.post("/message/", response_model=schemas.Message)
def create_message(
    message: schemas.MessageCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)
):
    return crud.create_message(db=db, message=message)


@app.delete("/message/", response_model=schemas.Message)
def delete_message(message_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    crud.delete_attachments_by_id(message_id=message_id, db=db)
    crud.delete_reactions(message_id=message_id, db=db)
    return crud.delete_message_by_id(db, message_id=message_id)


@app.get("/messages/", response_model=List[schemas.Message])
def get_messages(
    server_id: int = None, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db), limit: int = 100
):
    return crud.get_messages(server_id=server_id, channel_id=channel_id, user_id=user_id, db=db, limit=limit)


@app.get("/message/{message_id}", response_model=schemas.Message)
def get_message(message_id: int, db: Session = Depends(get_db)):
    return crud.get_message_by_id(db, message_id=message_id)


"""
    ATTACHMENT
"""


@app.post("/attachment/", response_model=schemas.Attachment)
def create_attachment(
    attachment: schemas.AttachmentCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)
):
    db_message = crud.get_attachment_by_url(db, url=attachment.url)
    if db_message:
        raise HTTPException(status_code=400, detail=f"Attachment [{attachment.url}] already exists!")
    return crud.create_attachment(db=db, attachment=attachment)


@app.delete("/attachment/", response_model=List[schemas.Attachment])
def delete_attachments(message_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
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
def create_reaction(
    reaction: schemas.ReactionCreate, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)
):
    return crud.create_reaction(db=db, reaction=reaction)


# TODO figure out this thing and have RESTful api, not delete via is_deleted=1 using app.post...
# @app.delete("/reaction/", response_model=schemas.Reaction)
# def delete_reaction(message_id: int = Path(...),
#                     reaction_id: int = Path(...),
#                     reacted_id: int = Path(...),
#                     db: Session = Depends(get_db)):
#     print(message_id, reacted_id, reaction_id)
#     return crud.delete_reaction_by_ids(db, message_id=message_id, reaction_id=reaction_id, reacted_id=reacted_id)


@app.delete("/reaction/{reaction_id}", response_model=schemas.Reaction)
def delete_reactions(message_id: int, db: Session = Depends(get_db), api_key: APIKey = Depends(get_api_key)):
    return crud.delete_reactions(message_id=message_id, db=db)


@app.get("/reactions/{message_id}", response_model=List[schemas.Reaction])
def get_reactions_by_id(message_id: int, db: Session = Depends(get_db)):
    return crud.get_reactions_by_message_id(message_id=message_id, db=db)


# @app.get("/reactions/", response_model=List[schemas.Reaction])
# def get_reactions(server_id: int, channel_id: int, reacted_id:int, db: Session = Depends(get_db)):
#     return crud.get_reactions(server_id=server_id, channel_id=channel_id, reacted_id=reacted_id, db=db)

"""
    CHART.JS QUERIES!
"""


@app.get("/charts/server-channel-messages/{server_id}")
def get_server_channel_messages(server_id: int, sort_by_position: bool = False, db: Session = Depends(get_db)):
    """
    Queries total messages for each channel for given server_id.
    Returns dictionary of labels and data for chart.js..

        Parameters:
            server_id: Discord server/guild id.
            sort_by_position: Default will sort channels by message amount, True will sort by their position in guild.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id):

        labels = []
        data = []
        positions = []

        query = db.query(models.Channel).filter_by(server_id=server_id, is_deleted=0).all()
        for channel in query:
            labels.append(channel.name)
            positions.append(channel.position)
            # Count amount of messages.
            data.append(db.query(models.Message).filter_by(channel_id=channel.id, is_deleted=0).count())

        if sort_by_position:
            positions, labels, data = zip(*sorted(zip(positions, labels, data)))
            return {"labels": labels, "data": data}
        else:
            data, labels = zip(*sorted(zip(data, labels)))
            return {"labels": labels[::-1], "data": data[::-1]}


@app.get("/stats/server-total-messages/{server_id}")
def get_server_total_messages(server_id: int, db: Session = Depends(get_db)):
    """"""
    if check_existence(db=db, server_id=server_id):
        messages = db.query(models.Message).filter_by(server_id=server_id, is_deleted=0).count()
        deleted = db.query(models.Message).filter_by(server_id=server_id, is_deleted=1).count()
        return {"server_id": server_id, "total_messages": messages, "total_deleted": deleted}


@app.get("/stats/server/{server_id}")
def get_server_stats(server_id: int, db: Session = Depends(get_db)):
    """"""
    if check_existence(db=db, server_id=server_id):
        # TODO add more fields to server like url, voice channels, whatever else
        server = db.query(models.Server).filter_by(id=server_id).first()
        owner = db.query(models.User).filter_by(id=server.owner_id).first()
        return {"server_id": server_id, "name": server.name, "owner_name": owner.username}


@app.get("/stats/messages-amount/")
def get_messages_total_days(
    server_id: int, channel_id: int = None, user_id: int = None, days: int = 0, db: Session = Depends(get_db)
):
    """
    Get amount of messages per server/channel/user/user+channel

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            days: Amount of days, 0 for today, 1 for yesterday, -1 for all.
            db: Database session.
        Returns:
            {"result": <amount of messages>}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        query = db.query(models.Message).filter_by(server_id=server_id, is_deleted=0)
        if channel_id:
            query = query.filter_by(channel_id=channel_id, is_deleted=0)
        if user_id:
            query = query.filter_by(author_id=user_id)
        # If user passes days as 0 or below 0, treat it as "query all days".
        if days >= 0:
            today = datetime.date.today()
            back = today - datetime.timedelta(days=days) if days > 0 else today
            # date = f"date >= DATETIME ('now', '-{days + 1} days') AND" if days >= 1 else ""
            query = query.filter(models.Message.date_utc >= back)
        return {"result": query.count()}


@app.get("/stats/messages-by-days/")
def get_messages_amount_days(
    days: int, server_id: int, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)
):
    """
    Returns date and amount of messages for that day. Can filter by server/channel/user/channel+user.
    Will query up to 90 days. Days where no messages are found will be added as 0.

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            days: Positive amount of days, 10 for past 10 days, 1 for today. Maximum of 90.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>], "average": <number>, "median": <number>}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_messages_amount_days(server_id=server_id, channel_id=channel_id, user_id=user_id, days=days, db=db)


@app.get("/stats/messages-by-weekday/")
def get_messages_by_weekday(
    server_id: int, days: int = -1, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)
):
    """
    Returns messages by weekday for server, channel, user or user in a channel.

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            days: Amount of days to query. Default is all. Negative will query all. Minimum is 2 days!
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_messages_by_weekday(
            db=db, server_id=server_id, channel_id=channel_id, days=days, user_id=user_id
        )


@app.get("/stats/messages-growth/")
def get_server_message_growth(
    server_id: int, days: int = 7, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)
):
    """
    Returns accumulated list of message growth for server, channel, user or user in channel per day.
    Uses the function above to get message counts per day and then accumulates them. So day 2 will have count for day 2
    and count of day 1. Day 3 will have day 2 + day 1...

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            days: Positive amount of days, 10 for past 10 days, 0/1 for today. Maximum of 90.
                  Negative numbers return 90 days. Default is 7 days.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_messages_growth_days(
            db=db, server_id=server_id, channel_id=channel_id, user_id=user_id, days=days
        )


@app.get("/stats/messages-growth-months/")
def get_server_message_growth_months(
    server_id: int, months: int = 6, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)
):
    """
    Returns a list of accumulative values for server/channel/user/user in a channel for a given amount of months.
    Amount of months can be specified. -1 returns all months since creation of the server (if messages are indexed).

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            months: Positive amount of months. 0 or negative number will query all data!
                    Default is 6 months.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_messages_growth_months(
            db=db, server_id=server_id, channel_id=channel_id, user_id=user_id, months=months
        )


@app.get("/stats/messages-by-hour/")
def get_server_messages_by_hour(
    server_id: int, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)
):
    """
    Calculates total amount messages by hour of day 00:00-23:00. Returns a dictionary of labels and according values.
    Queries all messages, does not calculate average or median!

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_messages_by_hour(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id)


@app.get("/stats/user-most-active/")
def get_user_most_active(
    server_id: int, days: int = -1, amount: int = 5, channel_id: int = None, db: Session = Depends(get_db)
):
    """
    Return most active users and their total messages for given amount of days.
    Can specify amount of days and users to query.

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            amount: Amount of users to query. Default is 5. Negative will query all.
            days: Amount of days to query. Default is all. Negative will query all.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id):
        return crud.get_user_most_active(db=db, server_id=server_id, channel_id=channel_id, days=days, amount=amount)


@app.get("/stats/reactions-today/{server_id}")
def get_reactions_today(server_id: int, db: Session = Depends(get_db)):
    """
    Get reactions given today.
        Parameters:
            server_id: Discord server/guild id.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id):
        return crud.get_reactions_today(db=db, server_id=server_id)


@app.get("/stats/reaction-stats/")
def get_reaction_stats(server_id: int, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)):
    """
    Returns a list of tuples for each reaction given by a user. If channel id is given, returns given reactions
    for that channel only. Otherwise reactions for all messages in the server.

        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id: Discord user id.
            db: Database session.
        Returns:
            {"labels": [<channel names>], "data": [<amount of messages>]}
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_reaction_given_counts(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id)


@app.get("/stats/heatmap/")
def get_heatmap(server_id: int, channel_id: int = None, user_id: int = None, db: Session = Depends(get_db)):
    """
    Returns a list of tuples (hour, weekday, amount of messages) for each hour and weekday of the week as a map.
    Considers all messages in the database for this query. Not limited by day.
    Used to build a heat map of message distribution by hour/weekday.
        Parameters:
            server_id: Discord server/guild id.
            channel_id: Discord channel id.
            user_id:
            db: Database session.
        Returns:
            TODO
    """
    if check_existence(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id):
        return crud.get_heatmap(db=db, server_id=server_id, channel_id=channel_id, user_id=user_id)
