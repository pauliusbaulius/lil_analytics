from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from api import crud


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
    server = crud.get_server_by_id(id=server_id, db=db)
    if not server:
        raise HTTPException(status_code=404, detail=f"server with id: {server_id} does not exist.")
    if channel_id:
        channel = crud.get_channel_by_id(db=db, id=channel_id)
        if not channel:
            raise HTTPException(status_code=404, detail=f"channel with id: {channel_id} does not exist.")
    if user_id:
        user = crud.get_user_by_id(db=db, user_id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"user with id: {user_id} does not exist.")
    return True


def get_conditional_where(server_id: int, channel_id: int = None, user_id: int = None) -> str:
    """Builds WHERE clause parameters for SQL query given guild, user, channel id combinations.
    If you want WHERE channel_id == ?, pass guild_id
    If you want WHERE channel_id == ? AND user_id == ?, pass guild_id and user_id
    Arguments:
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
