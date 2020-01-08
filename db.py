from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from config import Config

if Config.BOT_ENV == 'development':
    engine_uri = 'sqlite:///guilds.db'
else:
    engine_uri = Config.DATABASE_URI

engine = create_engine('sqlite:///guilds.db', echo=False)
Base = declarative_base()


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(Integer, primary_key=True, autoincrement=False)
    settings = relationship('Setting', backref='guild')


class Setting(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    value = Column(String(50), nullable=False)
    guild_id = Column(Integer, ForeignKey('guilds.id'))


class YoutubePlaylist(Base):
    __tablename__ = 'youtube_playlists'

    id = Column(Integer, primary_key=True)
    playlist_id = Column(String(50), nullable=False, unique=True)
    videos = relationship('PlaylistVideo', backref='playlist')


class PlaylistVideo(Base):
    __tablename__ = 'playlist_videos'

    id = Column(String(50), primary_key=True, autoincrement=False)
    video_id = Column(String(50), nullable=False, unique=True)
    playlist_id = Column(Integer, ForeignKey('youtube_playlists.id'))


def create_all():
    Base.metadata.create_all(engine)


session = sessionmaker(bind=engine)()
