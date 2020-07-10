from datetime import datetime

from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Table, BigInteger, ForeignKey, Integer, Column, String, DateTime, Boolean

guild_playlists = Table(
    'guild_playlists', Base.metadata,
    Column('guild_id', BigInteger, ForeignKey('guilds.id')),
    Column('playlist_id', Integer, ForeignKey('youtube_playlists.id'))
)


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    settings = relationship('Setting', backref='guild')
    moderations = relationship('Moderation')
    verification_roles = relationship('VerificationRole')
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


class Moderation(Base):
    __tablename__ = 'moderations'

    id = Column(Integer, primary_key=True)
    type = Column(String)
    user_id = Column(BigInteger)
    reason = Column(String)
    moderator_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
    expiration_date = Column(DateTime)
    creation_date = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

    @hybrid_property
    def expired(self):
        if self.expiration_date is None:
            return False
        return datetime.utcnow() > self.expiration_date


class VerificationRole(Base):
    __tablename__ = 'verification_roles'

    id = Column(Integer, primary_key=True)
    emoji = Column(String)
    role_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
