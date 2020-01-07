from dotenv import load_dotenv
import os
import json

load_dotenv()
TOKEN = os.environ.get('DISCORD_TOKEN')
YT_API_KEY = os.environ.get('YT_API_KEY')
BASE_PATH = os.environ.get('DISCORDBOT_BASE_PATH') or '.'


def get_prefix(bot, msg):
    guild_id = str(msg.guild.id)
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    try:
        prefix = config[guild_id]['prefix']
    except KeyError:
        prefix = config['default']['prefix']
    return prefix


def set_prefix(msg, *args):
    guild_id = str(msg.guild.id)
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    try:
        config[guild_id]
    except KeyError:
        config[guild_id] = {}
    if len(args) == 1 and args[0] == '!' and list(config[guild_id].keys()) == ['prefix']:
        config.pop(guild_id, None)
    else:
        config[guild_id]['prefix'] = list(args)
    with open(os.path.join(BASE_PATH, 'config.json'), 'w') as file:
        json.dump(config, file, indent=2)


def add_to_playlist_cache(playlist_id, video_id):
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    yt_playlists = config['default'].get('yt playlists')
    if yt_playlists is None:
        config['default']['yt playlists'] = dict()
    playlist_videos = config['default']['yt playlists'].get(playlist_id)
    if playlist_videos is None:
        config['default']['yt playlists'][playlist_id] = list()
    playlist_videos = config['default']['yt playlists'].get(playlist_id)
    if len(playlist_videos) > 10:
        for _ in range(5):
            playlist_videos.pop()
    if video_id not in playlist_videos:
        playlist_videos.append(video_id)
    with open(os.path.join(BASE_PATH, 'config.json'), 'w') as file:
        json.dump(config, file, indent=2)


def get_playlist_cache(playlist_id: str):
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    try:
        videos = config['default']['yt playlists'][playlist_id]
    except:
        return list()
    else:
        return videos


def set_yt_notifier_channel(guild_id, channel_id):
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    try:
        config[guild_id]
    except KeyError:
        config[guild_id] = {}
    config[guild_id]['yt notifier channel'] = channel_id
    with open(os.path.join(BASE_PATH, 'config.json'), 'w') as file:
        json.dump(config, file, indent=2)


def get_yt_notifier_channel(guild_id):
    guild_id = str(guild_id)
    with open(os.path.join(BASE_PATH, 'config.json')) as file:
        config = json.load(file)
    try:
        notifier_channel = config[guild_id]['yt notifier channel']
    except KeyError:
        return None
    else:
        return notifier_channel


if __name__ == "__main__":
    print(get_yt_notifier_channel('663834937606012962'))
    print(get_playlist_cache('UUvnoM0R1sDKm-YCPifEso_g'))
