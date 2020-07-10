import logging

from ..bot import Bot
from .. import crud, youtube
from ..config import Settings
from ..database import session_factory

from sqlalchemy.orm import Session
from discord.ext import commands, tasks


class Loops(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.youtube_notifier.start()

    def cog_unload(self):
        self.youtube_notifier.cancel()

    @tasks.loop(minutes=Settings.LOOP_MINUTES)
    async def youtube_notifier(self):
        if Settings.YOUTUBE_API_KEY is None:
            return
        db: Session = session_factory()
        for playlist in crud.get_all_playlists(db):
            playlist_guilds = playlist.guilds
            if not playlist_guilds:
                crud.delete_playlist(playlist, db)
                continue
            videos = await youtube.get_playlist_videos_id(self.bot.session, playlist.playlist_id)
            for video_id in videos:
                if crud.get_video(video_id, db):
                    continue
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                for db_guild in playlist_guilds:
                    guild = self.bot.get_guild(db_guild.id)
                    try:
                        channel_id = int(crud.get_guild_setting(db_guild, 'notifications_channel', db))
                    except TypeError:
                        await guild.system_channel.send('Por favor elige un canal para las notificaciones de videos '
                                                        'usando `setchannel youtube #canal`')
                        continue
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(video_url)

                crud.add_video(playlist, video_id, db)

        db.close()

    @youtube_notifier.before_loop
    async def before_notifier(self):
        await self.bot.wait_until_ready()
