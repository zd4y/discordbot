import re
import discord
from discord.ext import commands

from .. import crud
from ..bot import Bot
from ..utils import fetch
from ..config import Settings


# TODO Put the help and aliases in the commands here
class ServerConfigCmds(commands.Cog, name='Configuraciones del bot para el servidor'):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return ('manage_guild', True) in ctx.author.permissions_in(ctx.channel)

    @commands.group(help='Personaliza al bot para el servidor', invoke_without_command=True)
    async def config(self, ctx: commands.Context):
        # TODO Display a message showing what can be done with this command
        pass

    @config.command(
        help='Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos separados por un espacio',
        usage='[nuevos prefixes]'
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context, *, new_prefixes: str = ''):
        if new_prefixes:
            crud.set_guild_setting(ctx.guild.id, 'prefix', new_prefixes)
            embed = discord.Embed(
                title='Prefix editado! ✅',
                description=f'Los prefixes ahora son: {new_prefixes}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            guild = crud.get_guid(ctx.guild.id)
            prefixes = crud.get_guild_setting(guild, 'prefix')
            if isinstance(prefixes, list):
                prefixes = ' '.join(prefixes)
            embed = discord.Embed(
                title='Prefix del Bot',
                description=f'Los prefixes actuales son: {prefixes}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @config.group(help='Configuración sobre las noticiaciones de youtube', aliases=['youtube'], invoke_without_command=True)
    async def yt(self, ctx: commands.Context):
        embed = discord.Embed(
            title='Configuración de YT Notifier',
            color=discord.Color.red()
        )
        embed.add_field(
            name='Canal', value=f'Puedes configurar el canal de texto al cual se enviaran las notificaciones usando `{ctx.prefix}config yt set channel #canal`', inline=False)
        embed.add_field(name='Seguir un canal de YouTube',
                        value=f'Para seguir un canal de youtube y recibir notificaciones de sus nuevos videos, usa `{ctx.prefix}config yt add channel <canal>`. Para más información usa `{ctx.prefix}help config yt add channel`\n\nTambién puedes usar `{ctx.prefix}config yt remove playlist <id>` para eliminar un canal (Puedes ver la id de las playlists más abajo)\n\u200b', inline=False)

        guild = crud.get_guid(ctx.guild.id)
        notifications_channel = crud.get_guild_setting(guild, 'notifications_channel')
        try:
            notifications_channel = int(notifications_channel)
        except (TypeError, ValueError):
            notifications_channel = 'Ninguno'
        else:
            notifications_channel = discord.utils.get(ctx.guild.channels, id=notifications_channel).mention

        value = f'El canal para notificaciones es: {notifications_channel}'
        db_guild = crud.get_guid(ctx.guild.id)
        if db_guild:
            followed_playlists = db_guild.youtube_playlists
        else:
            followed_playlists = None
        if followed_playlists:
            value += '\nLa id de las playlists seguidas son:'
            for playlist in followed_playlists:
                channel_title = playlist.channel
                if channel_title is None:
                    url = 'https://www.googleapis.com/youtube/v3/playlistItems'
                    params = {
                        'part': 'snippet',
                        'maxResults': 1,
                        'playlistId': playlist.playlist_id,
                        'key': Settings.YOUTUBE_API_KEY
                    }
                    channel_title = (await fetch(self.bot.session, url, params=params))['items'][0]['snippet']['channelTitle']
                value += f'\n{playlist.id}) Videos de {channel_title}'
        else:
            value += '\nActualmente no sigues ninguna playlist ni canal'
        embed.add_field(name='Configuraciones Actuales', value=value)
        await ctx.send(embed=embed)

    @yt.group(name='set', invoke_without_command=True)
    async def set_(self, ctx: commands.Context):
        # TODO Display a message showing what can be done with this command
        pass

    @set_.command(help='Coloca el canal al cual se enviaran las novedades (nuevos videos canales de YouTube configurados)')
    async def channel(self, ctx: commands.Context, channel: discord.TextChannel):
        crud.set_guild_setting(ctx.guild.id, 'notifications_channel', str(channel.id))
        embed = discord.Embed(
            title='Canal colocado! ✅',
            description='El canal para las novedades ha sido colocado satisfactoriamente.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @yt.group(invoke_without_command=True)
    async def add(self, ctk: commands.Context):
        # TODO Display a message showing what can be done with this command
        pass

    @add.command(name='channel')
    async def channel_(self, ctx: commands.Context, *, yt_channel: str):
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        is_url = bool(pattern.search(yt_channel))
        if is_url:
            channel_id = yt_channel.split('/')[-1]
        else:
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'type': 'channel',
                'maxResults': 1,
                'q': yt_channel,
                'key': Settings.YOUTUBE_API_KEY
            }
            channel_id = (await fetch(self.bot.session, url, params=params))['items'][0]['snippet']['channelId']

        url = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'snippet,contentDetails',
            'id': channel_id,
            'key': Settings.YOUTUBE_API_KEY
        }
        channel = (await fetch(self.bot.session, url, params=params))['items'][0]
        channel_playlist = channel['contentDetails']['relatedPlaylists']['uploads']
        channel_info = channel['snippet']
        channel_title = channel_info['title']

        db_guild = crud.get_or_create_guild(ctx.guild.id)
        crud.add_playlist(guild=db_guild, playlist_id=channel_playlist, channel=channel_title)

        embed = discord.Embed(
            title='Canal Agregado! ✅',
            description=f'El canal {channel_title} ha sido agregado correctamente!',
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=channel_info['thumbnails']['default']['url'])
        await ctx.send(embed=embed)

    @yt.group(invoke_without_command=True)
    async def remove(self, ctx: commands.Context):
        # TODO Show a message
        pass

    # TODO: Use an integer instead of the playlist_id
    @remove.command()
    async def playlist(self, ctx: commands.Context, num: int):
        guild = crud.get_or_create_guild(ctx.guild.id)
        playlist = crud.get_playlist(db_id=num)
        guild.youtube_playlists.remove(playlist)
        if not playlist.guilds:
            crud.delete_playlist(playlist)

        embed = discord.Embed(
            title='Playlist eliminada! ✅',
            description='La playlist ha sido eliminada correctamente.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
