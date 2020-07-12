from . import Base

from sqlalchemy import BigInteger, ForeignKey, Integer, Column, String


class VerificationRole(Base):
    __tablename__ = 'verification_roles'

    id = Column(Integer, primary_key=True)
    emoji = Column(String)
    role_id = Column(BigInteger)
    guild_id = Column(BigInteger, ForeignKey('guilds.id'))
