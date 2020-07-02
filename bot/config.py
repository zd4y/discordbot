import os
import json
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LOOP_MINUTES = int(os.environ['LOOP_MINUTES'])
    DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
    DEFAULT_SETTINGS = json.loads(os.environ['DEFAULT_SETTINGS'])
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///guilds.db')
    DEVELOPERS_ID = json.loads(os.environ.get('DEVELOPERS_ID', '[]'))
