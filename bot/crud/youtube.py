from typing import Optional

from sqlalchemy.orm import Session

from . import get_query, get, get_or_create, find, create_one
from ..database import session
from ..models import YoutubePlaylist, YoutubeVideo, Guild


def get_video(video_id: str, db: Optional[Session] = None):
    return find(model=YoutubeVideo, db=db, video_id=video_id)


def get_all_playlists(db: Optional[Session]):
    query = get_query(YoutubePlaylist, db)
    return query.all()


def get_playlist(playlist_id: Optional[str] = None, db_id: Optional[int] = None):
    if not db_id and not playlist_id:
        raise ValueError('At least one argument is required.')
    if db_id:
        return get(model=YoutubePlaylist, obj_id=db_id)
    return find(model=YoutubePlaylist, playlist_id=playlist_id)


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
