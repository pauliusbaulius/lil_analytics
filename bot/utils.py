"""
Utility functions that are used by many cogs and modules.
"""
import os


def is_me(mentions: "list of mentions") -> bool:
    """Checks whether mentions contain this bot's id."""
    for mention in mentions:
        if mention.id == os.environ["BOT_ID"]:
            return True


def is_owner(user_id: "user id as integer") -> bool:
    """Checks whether given user_id matches bot owners id. Useful to check before executing critical commands,
    like cog loading. There is a decorator commands.is_owner(), but it won't work if you have a dedicated Discord
    account for bots and use different account for personal use. This solves it.
    """
    return user_id == os.environ["BOT_OWNER_ID"]
