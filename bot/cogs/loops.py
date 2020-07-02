import logging

from .. import crud
from ..bot import Bot
from ..utils import fetch
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
        logging.info('starting yt notifier')
        db: Session = session_factory()
        for playlist in crud.get_all_playlists(db):
            playlist_guilds = playlist.guilds
            if not playlist_guilds:
                crud.delete_playlist(playlist, db)
                continue
            logging.info(f'starting with playlist_id: {playlist.playlist_id}')
            url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            params = {
                'part': 'snippet,contentDetails',
                'maxResults': 5,
                'playlistId': playlist.playlist_id,
                'key': Settings.YOUTUBE_API_KEY
            }
            videos = (await fetch(self.bot.session, url, params=params))['items'][::-1]
            logging.info(f'got {len(videos)} videos')
            for video in videos:
                video_id = video['snippet']['resourceId']['videoId']
                logging.info(f'checking the cache for the video: {video_id}')
                db_video = crud.get_video(video_id, db)
                if db_video:
                    logging.info('video was in cache, skipping')
                    continue
                logging.info('video was not in cache! sending message to the channel')
                video_url = 'https://www.youtube.com/watch?v=' + video_id
                for db_guild in playlist_guilds:
                    guild = self.bot.get_guild(db_guild.id)
                    logging.info(f'notifying guild: {guild.name}')
                    try:
                        channel_id = int(crud.get_guild_setting(db_guild, 'notifications_channel', db))
                    except TypeError:
                        logging.info('channel not found!')
                        await guild.system_channel.send('Por favor elige un canal para las notificaciones de videos usando `config yt set channel #canal`')
                        continue
                    channel = self.bot.get_channel(channel_id)
                    await channel.send(video_url)
                    logging.info('message sent')

                crud.add_video(playlist, video_id, db)

        db.close()

    @youtube_notifier.before_loop
    async def before_notifier(self):
        await self.bot.wait_until_ready()
