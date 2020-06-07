from . import crud
from .database import session
from functools import wraps
from discord.ext.commands import when_mentioned_or


def get_prefix(bot, msg):
    guild = crud.get_guid(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, 'prefix')
    prefixes = prefix_setting.split()
    return when_mentioned_or(*prefixes)(bot, msg)


def to_bool(s: str):
    return s.lower() in ('1', 'true', 'on')


def to_str_bool(b: bool):
    if b is True:
        return '1'
    return '0'


def use_db(func: callable):
    @wraps(func)
    async def decorator(*args, **kwargs):
        session()
        value = await func(*args, **kwargs)
        session.remove()
        return value
    return decorator
