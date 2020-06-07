from typing import Optional
from sqlalchemy.orm import Session

from .config import Settings
from .database import Base, session
from .models import YoutubePlaylist, YoutubeVideo, Guild, Setting


def get_query(model: Base, db: Optional[Session] = None):
    if db:
        return db.query(model)
    return model.query


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


def get_guid(guild_id):
    return get_by_id(model=Guild, obj_id=guild_id)


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


def create_guild(guild_id: int):
    return create_one(Guild, id=guild_id)


def get_or_create_guild(guild_id: int):
    return get_or_create(model=Guild, id=guild_id)


def get_playlist(playlist_id: str):
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
    return Settings.DEFAULT_SETTINGS.get(setting_name)


def set_guild_setting(guild_id: int, setting_name: str, setting_value: str):
    guild = get_or_create_guild(guild_id)
    setting = get_guild_setting(guild, setting_name, as_db=True)
    if setting:
        setting.value = setting_value
        session.commit()
    else:
        create_guild_setting(guild, setting_name, setting_value)
    return setting

