from ..models import Guild
from . import get_or_create


def get_guild(guild_id):
    return get_or_create(Guild, None, id=guild_id)
