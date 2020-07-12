from . import create_one
from ..database import session
from ..models import VerificationRole


def add_verification_role(guild_id: int, role_id: int, emoji: str):
    create_one(VerificationRole, guild_id=guild_id, role_id=role_id, emoji=emoji)


def remove_verification_role(role_id: int):
    role = VerificationRole.query.get(role_id)
    session.delete(role)
    session.commit()


def get_verification_roles(guild_id: int):
    return VerificationRole.query.filter_by(guild_id=guild_id).all()


def get_role_by_emoji(guild_id: int, emoji: str):
    return VerificationRole.query.filter_by(guild_id=guild_id, emoji=emoji).first()
