"""add revoked to moderation

Revision ID: 98e4a6da98fe
Revises: 4c931b665b4f
Create Date: 2020-07-10 13:54:43.766538

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '98e4a6da98fe'
down_revision = '4c931b665b4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('moderations', sa.Column('revoked', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('moderations', 'revoked')
    # ### end Alembic commands ###
