from . import Base

from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import BigInteger, ForeignKey, Integer, Column, String, DateTime, Boolean


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
