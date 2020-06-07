from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Table, BigInteger, ForeignKey, Integer, Column, String


guild_playlists = Table(
    'guild_playlists', Base.metadata,
    Column('guild_id', BigInteger, ForeignKey('guilds.id')),
    Column('playlist_id', Integer, ForeignKey('youtube_playlists.id'))
)


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    settings = relationship('Setting', backref='guild')
    youtube_playlists = relationship('YoutubePlaylist', secondary=guild_playlists, back_populates='guilds')


class Setting(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    value = Column(String(500), nullable=False)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))


playlist_videos = Table(
    'playlist_videos', Base.metadata,
    Column('playlist_id', BigInteger, ForeignKey('youtube_playlists.id')),
    Column('video_id', Integer, ForeignKey('youtube_videos.id'))
)


class YoutubePlaylist(Base):
    __tablename__ = 'youtube_playlists'

    id = Column(Integer, primary_key=True)
    channel = Column(String(100))
    playlist_id = Column(String(50), nullable=False, unique=True)
    guilds = relationship('Guild', secondary=guild_playlists, back_populates='youtube_playlists')
    videos = relationship('YoutubeVideo', secondary=playlist_videos, back_populates='playlists')


class YoutubeVideo(Base):
    __tablename__ = 'youtube_videos'

    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), nullable=False, unique=True)
    playlists = relationship('YoutubePlaylist', secondary=playlist_videos, back_populates='videos')
