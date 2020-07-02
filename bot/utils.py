from . import crud
from .config import Settings

from aiohttp import ClientSession
from discord import Message
from discord.ext.commands import Bot, Context, when_mentioned_or, check


def get_prefix(bot: Bot, msg: Message):
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


async def fetch(session: ClientSession, url: str, **kwargs) -> dict:
    async with session.get(url, **kwargs) as res:
        return await res.json()
