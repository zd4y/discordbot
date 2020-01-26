import os
from . import db

import logging

logging.basicConfig(filename='latest.log', level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if '.env' in os.listdir(PATH):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(PATH, '.env'))


class Config:
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')


class ServerConfig:
    @staticmethod
    async def get_default_setting(name, default=None):
        default_settings = {
            'prefix': '!',
            'debug': False
            # 'followed_playlists': 'UUvnoM0R1sDKm-YCPifEso_g' (Absolute uploads)
            # 'notifications_channel': channel id
        }
        return default_settings.get(name, default)

    @classmethod
    async def get_setting(cls, guild_id: int, name: str, default=None):
        guild = db.session.query(db.Guild).filter_by(id=guild_id).first()
        if guild:
            for setting in guild.settings:
                if setting.name == name:
                    return setting.value
        return await cls.get_default_setting(name, default)

    @classmethod
    async def set_setting(cls, guild_id: int, name: str, value: str):
        guild = db.session.query(db.Guild).filter_by(id=guild_id).first()
        if guild is None:
            guild = db.Guild(id=guild_id)
            db.session.add(guild)
        already_existed = False
        for setting in guild.settings:
            if setting.name == name:
                setting.value = value
                already_existed = True
        if already_existed is False:
            setting = db.Setting(name=name, value=value, guild=guild)
            db.session.add(setting)
        db.session.commit()
        return setting


class YoutubeVideos:
    @staticmethod
    async def add_videos(playlist_id, videos: list):
        playlist = db.session.query(db.YoutubePlaylist).filter_by(playlist_id=playlist_id).first()
        if playlist is None:
            playlist = db.YoutubePlaylist(playlist_id=playlist_id)
            db.session.add(playlist)
        for video_id in videos:
            db_video = db.session.query(db.PlaylistVideo).filter_by(video_id=video_id).first()
            if db_video is None:
                db_video = db.PlaylistVideo(video_id=video_id, playlist=playlist)
                db.session.add(db_video)
        db.session.commit()

    @staticmethod
    async def get_videos() -> list:
        return map(lambda video: video.video_id, db.session.query(db.PlaylistVideo).all())

    @staticmethod
    async def get_playlists() -> list:
        return map(lambda playlist: playlist.playlist_id, db.session.query(db.YoutubePlaylist).all())
