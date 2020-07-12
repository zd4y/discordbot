from . import Base
from .relationships import playlist_videos

from sqlalchemy.orm import relationship
from sqlalchemy import Integer, Column, String


class YoutubeVideo(Base):
    __tablename__ = 'youtube_videos'

    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), nullable=False, unique=True)
    playlists = relationship('YoutubePlaylist', secondary=playlist_videos, back_populates='videos')
