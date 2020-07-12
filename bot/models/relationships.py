from . import Base

from sqlalchemy import Table, BigInteger, ForeignKey, Integer, Column


guild_playlists = Table(
    'guild_playlists', Base.metadata,
    Column('guild_id', BigInteger, ForeignKey('guilds.id')),
    Column('playlist_id', Integer, ForeignKey('youtube_playlists.id'))
)


playlist_videos = Table(
    'playlist_videos', Base.metadata,
    Column('playlist_id', BigInteger, ForeignKey('youtube_playlists.id')),
    Column('video_id', Integer, ForeignKey('youtube_videos.id'))
)
