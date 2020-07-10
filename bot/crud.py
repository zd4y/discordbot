from typing import Optional
from datetime import datetime
from discord import TextChannel
from discord.ext.commands import Bot

from sqlalchemy.orm import Session

from .config import Settings
from .database import Base, session
from .models import YoutubePlaylist, YoutubeVideo, Guild, Setting, Moderation, VerificationRole


def get_query(model: Base, db: Optional[Session] = None):
    return db.query(model) if db else model.query


def get(model: Base, db: Optional[Session] = None, **kwargs):
    if not kwargs:
        raise TypeError('You must provide at least one keyword argument')
    query = get_query(model, db)
    return query.filter_by(**kwargs).first()


def get_by_id(model: Base, obj_id: int):
    return model.query.get(obj_id)


def get_video(video_id: str, db: Optional[Session] = None):
    return get(model=YoutubeVideo, db=db, video_id=video_id)


def get_all_playlists(db: Optional[Session]):
    query = get_query(YoutubePlaylist, db)
    return query.all()


def create_one(model: Base, db: Optional[Session] = None, **kwargs):
    obj = model(**kwargs)
    if db is None:
        db = session
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_or_create(model: Base, db: Optional[Session] = None, **kwargs):
    obj = get(model, db, **kwargs)
    if obj is None:
        obj = create_one(model, db, **kwargs)
    return obj


def get_guid(guild_id):
    return get_or_create(Guild, None, id=guild_id)


def create_guild(guild_id: int):
    return create_one(Guild, id=guild_id)


def get_or_create_guild(guild_id: int):
    return get_or_create(model=Guild, id=guild_id)


def get_playlist(playlist_id: Optional[str] = None, db_id: Optional[int] = None):
    if not db_id and not playlist_id:
        raise ValueError('At least one argument is required.')
    if db_id:
        return get_by_id(model=YoutubePlaylist, obj_id=db_id)
    return get(model=YoutubePlaylist, playlist_id=playlist_id)


def get_or_create_playlist(playlist_id: str):
    return get_or_create(model=YoutubePlaylist, playlist_id=playlist_id)


def delete_playlist(playlist: YoutubePlaylist, db: Optional[Session] = None):
    if db is None:
        db = session
    db.delete(playlist)
    db.commit()


def create_playlist(playlist_id: str, channel: str):
    return create_one(YoutubePlaylist, playlist_id=playlist_id, channel=channel)


def add_playlist(guild: Guild, playlist_id: str, channel: str):
    playlist = get_playlist(playlist_id)
    if playlist is None:
        playlist = create_playlist(playlist_id=playlist_id, channel=channel)
    guild.youtube_playlists.append(playlist)
    session.commit()


def add_video(playlist: YoutubePlaylist, video_id: str, db: Optional[Session] = None):
    video = get_or_create(YoutubeVideo, db, video_id=video_id)
    video.playlists.append(playlist)
    session.commit()
    return video


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
    guild = get_or_create_guild(guild_id)
    setting = get_guild_setting(guild, setting_name, as_db=True)
    if setting:
        setting.value = setting_value
        session.commit()
    else:
        create_guild_setting(guild, setting_name, setting_value)
    return setting


def get_channel_setting(
        bot: Bot, guild: Guild, setting_name: str, db: Optional[Session] = None
) -> Optional[TextChannel]:
    channel_id = get_guild_setting(guild, setting_name, db)

    channel = None
    if channel_id and channel_id.isdigit():
        channel = bot.get_channel(int(channel_id))

    return channel


def moderate(
        moderation_type: str,
        user_id: int,
        date: datetime,
        expiration_date: datetime,
        guild_id: int,
        moderator_id: int,
        reason: str = ''
) -> None:
    create_one(
        Moderation,
        type=moderation_type,
        user_id=user_id,
        moderator_id=moderator_id,
        reason=reason,
        creation_date=date,
        expiration_date=expiration_date,
        guild_id=guild_id
    )


def get_moderation(moderation_type: str, user_id: int, guild_id: int):
    return (
        Moderation
        .query
        .filter_by(type=moderation_type, user_id=user_id, guild_id=guild_id)
        .order_by(Moderation.id.desc())
        .first()
    )


def get_moderations(moderation_type: str, user_id: int, guild_id: int):
    return (
        Moderation
        .query
        .filter_by(type=moderation_type, user_id=user_id, guild_id=guild_id)
        .order_by(Moderation.id.desc())
        .all()
    )


def get_all_moderations(guild_id: int, user_id: Optional[int] = None, revoked: Optional[bool] = None):
    query = (
        Moderation
        .query
        .filter_by(guild_id=guild_id)
    )

    if user_id:
        query = query.filter_by(user_id=user_id)

    if revoked is not None:
        query = query.filter(Moderation.revoked == revoked, Moderation.expiration_date.isnot(None))

    return query.order_by(Moderation.id.desc()).all()


def revoke_moderation(moderation: Moderation):
    moderation.revoked = True
    session.commit()


def add_verification_role(guild_id: int, role_id: int, emoji: str):
    create_one(VerificationRole, guild_id=guild_id, role_id=role_id, emoji=emoji)


def remove_verification_role(role_id: int):
    role = VerificationRole.query.get(role_id)
    session.delete(role)
    session.commit()


def get_verification_roles(guild_id: int):
    return VerificationRole.query.filter_by(guild_id=guild_id).all()


def get_role_by_emoji(guild_id: int, emoji: str):
    return VerificationRole.query.filter_by(guild_id=guild_id, emoji=emoji).first()
