import re
from aiohttp import ClientSession


def to_bool(s: str):
    return s.lower() in ('1', 'true', 'on') if s else False


def to_str_bool(b: bool):
    if b is True:
        return '1'
    return '0'


url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def is_url(s: str):
    return bool(url_pattern.search(s))


async def fetch(session: ClientSession, url: str, **kwargs) -> dict:
    async with session.get(url, **kwargs) as res:
        return await res.json()


def callback(func, *args, **kwargs):
    async def inner(*_, **__):
        return await func(*args, **kwargs)
    return inner
