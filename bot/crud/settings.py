from typing import Optional
from discord import TextChannel
from discord.ext.commands import Bot

from sqlalchemy.orm import Session

from . import get_query, get_guild
from ..config import Settings
from ..database import session
from ..models import Guild, Setting


def create_guild_setting(guild: Guild, setting_name: str, setting_value: str):
    setting = Setting(name=setting_name, value=setting_value, guild=guild)
    session.add(setting)
    session.commit()


def get_guild_setting(guild: Guild, setting_name: str, db: Optional[Session] = None, as_db=False):
    query = get_query(Setting, db)
    setting = query.filter(Setting.guild == guild, Setting.name == setting_name).first()
    if as_db:
        return setting
    elif setting:
        return setting.value
    default = Settings.DEFAULT_SETTINGS.get(setting_name)
    return str(default) if default else None


def set_guild_setting(guild_id: int, setting_name: str, setting_value: str):
    guild = get_guild(guild_id)
    setting = get_guild_setting(guild, setting_name, as_db=True)
    if setting:
        setting.value = setting_value
        session.commit()
    else:
        create_guild_setting(guild, setting_name, setting_value)
    return setting


def get_set_channel(
        bot: Bot, guild: Guild, setting_name: str, db: Optional[Session] = None
) -> Optional[TextChannel]:
    channel_id = get_guild_setting(guild, setting_name, db)

    channel = None
    if channel_id and channel_id.isdigit():
        channel = bot.get_channel(int(channel_id))

    return channel
