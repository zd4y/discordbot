import os
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, Table


DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///guilds.db'

engine = create_engine(DATABASE_URI, echo=False)
Base = declarative_base()


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


def create_all():
    Base.metadata.create_all(engine)


session = sessionmaker(bind=engine)()


async def get(model, **kwargs):
    if kwargs is None:
        raise TypeError('You must provide at least one key word argument')
    return session.query(model).filter_by(**kwargs).first()
