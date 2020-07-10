"""change Moderations table

Revision ID: ae568817f1c0
Revises: 
Create Date: 2020-07-09 22:44:00.753652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae568817f1c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('guilds',
    sa.Column('id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('youtube_playlists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('channel', sa.String(length=100), nullable=True),
    sa.Column('playlist_id', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('playlist_id')
    )
    op.create_table('youtube_videos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('video_id', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('video_id')
    )
    op.create_table('guild_playlists',
    sa.Column('guild_id', sa.BigInteger(), nullable=True),
    sa.Column('playlist_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.ForeignKeyConstraint(['playlist_id'], ['youtube_playlists.id'], )
    )
    op.create_table('moderations',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.Column('user_id', sa.BigInteger(), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('moderator_id', sa.BigInteger(), nullable=True),
    sa.Column('guild_id', sa.BigInteger(), nullable=True),
    sa.Column('expiration_date', sa.DateTime(), nullable=True),
    sa.Column('creation_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('playlist_videos',
    sa.Column('playlist_id', sa.BigInteger(), nullable=True),
    sa.Column('video_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['playlist_id'], ['youtube_playlists.id'], ),
    sa.ForeignKeyConstraint(['video_id'], ['youtube_videos.id'], )
    )
    op.create_table('settings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('value', sa.String(length=500), nullable=False),
    sa.Column('guild_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('verification_roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emoji', sa.String(), nullable=True),
    sa.Column('role_id', sa.BigInteger(), nullable=True),
    sa.Column('guild_id', sa.BigInteger(), nullable=True),
    sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('verification_roles')
    op.drop_table('settings')
    op.drop_table('playlist_videos')
    op.drop_table('moderations')
    op.drop_table('guild_playlists')
    op.drop_table('youtube_videos')
    op.drop_table('youtube_playlists')
    op.drop_table('guilds')
    # ### end Alembic commands ###
