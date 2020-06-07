from . import crud
from inspect import ismethod
from functools import wraps
from .database import session_factory
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
        db = session_factory()
        if ismethod(func):
            value = await func(args[0], db, *args[1:], **kwargs)
        else:
            value = await func(db, *args, **kwargs)
        db.close()
        return value
    return decorator
