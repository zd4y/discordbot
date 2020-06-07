from . import crud
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
