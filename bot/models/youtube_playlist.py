from . import Base
from .relationships import guild_playlists, playlist_videos

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String


class YoutubePlaylist(Base):
    __tablename__ = 'youtube_playlists'

    id = Column(Integer, primary_key=True)
    channel = Column(String(100))
    playlist_id = Column(String(50), nullable=False, unique=True)
    guilds = relationship('Guild', secondary=guild_playlists, back_populates='youtube_playlists')
    videos = relationship('YoutubeVideo', secondary=playlist_videos, back_populates='playlists')
