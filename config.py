import os
import db

if '.env' in os.listdir():
    from dotenv import load_dotenv
    load_dotenv()


class Config:
    DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    BOT_ENV = os.environ.get('BOT_ENV').lower()  # This can be either development or production
    DATABASE_URI = os.environ.get('DATABASE_URI')


class ServerConfig:
    @staticmethod
    def get_default_setting(name):
        default_settings = {
            'prefix': '!'
            # 'followed_playlists': 'UUvnoM0R1sDKm-YCPifEso_g' (Absolute uploads)
            # 'notifications_channel': channel id
        }
        return default_settings.get(name)

    @classmethod
    def get_setting(cls, guild_id: int, name: str):
        guild = db.session.query(db.Guild).filter_by(id=guild_id).first()
        if guild:
            for setting in guild.settings:
                if setting.name == name:
                    return setting.value
        return cls.get_default_setting(name)

    @classmethod
    def set_setting(cls, guild_id: int, name: str, value: str):
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


class YoutubeVideos:
    @staticmethod
    def add_videos(playlist_id, videos: list):
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
    def get_videos() -> list:
        return map(lambda video: video.video_id, db.session.query(db.PlaylistVideo).all())

    @staticmethod
    def get_playlists() -> list:
        return map(lambda playlist: playlist.playlist_id, db.session.query(db.YoutubePlaylist).all())
