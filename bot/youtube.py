import asyncio

from .utils import fetch
from .config import Settings
from aiohttp import ClientSession


base_url = 'https://www.googleapis.com/youtube/v3/{}'


async def fetch_youtube(session: ClientSession, resource: str, part: str, **kwargs) -> dict:
    params = {
        'part': part,
        'key': Settings.YOUTUBE_API_KEY,
        **kwargs
    }

    url = base_url.format(resource)
    json = await fetch(session, url, params=params)

    return json


async def search_channel(session: ClientSession, query: str) -> str:
    json = await fetch_youtube(session, 'search', 'id', type='channel', maxResults=1, q=query)
    result = json['items'][0]['id']['channelId']

    return result


async def fetch_channel(session: ClientSession, channel_id: str, snippet=False):
    part = 'contentDetails'
    if snippet:
        part += ',snippet'

    json = await fetch_youtube(session, 'channels', part, id=channel_id)
    channel = json['items'][0]
    print(channel)
    return channel


async def get_channel_playlists(session: ClientSession, channel_id: str):
    channel = await fetch_channel(session, channel_id)
    channel_playlist = channel['contentDetails']['relatedPlaylists']['uploads']

    return channel_playlist


async def get_playlist_videos(session: ClientSession, playlist_id: str, max_results: int = 5) -> list:
    json = await fetch_youtube(session, 'playlistItems', 'snippet,contentDetails', playlistId=playlist_id, maxResults=max_results)
    videos = json['items'][::-1]

    return videos


async def get_playlist_videos_id(session: ClientSession, channel_id: str):
    videos = await get_playlist_videos(session, channel_id)
    return map(lambda video: video['snippet']['resourceId']['videoId'], videos)


async def main():
    async with ClientSession() as session:
        channel_id = await search_channel(session, 'test')
        channel = await fetch_channel(session, channel_id)
        print(channel)


if __name__ == '__main__':
    asyncio.run(main())
