from . import Base
from .relationships import guild_playlists

from sqlalchemy.orm import relationship
from sqlalchemy import BigInteger, Column


class Guild(Base):
    __tablename__ = 'guilds'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    settings = relationship('Setting', backref='guild')
    moderations = relationship('Moderation')
    verification_roles = relationship('VerificationRole')
    youtube_playlists = relationship('YoutubePlaylist', secondary=guild_playlists, back_populates='guilds')
