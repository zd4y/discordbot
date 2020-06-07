import re
import discord
import logging

from . import crud
from .bot import Bot
from typing import Optional
from .config import Settings
from discord.ext import commands, tasks
from .database import session_factory
from .utils import to_str_bool, to_bool

from sqlalchemy.orm import Session


async def fetch(session, url, **kwargs):
    async with session.get(url, **kwargs) as res:
        return await res.json()


class Listeners(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game('prefix: !')
        await self.bot.change_presence(activity=activity)
        logging.info('Bot is ready')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return

        # TODO Get the welcoming_channel from server settings
        channel = member.guild.system_channel
        default_role = discord.utils.get(member.guild.roles, name='Miembro')
        await member.add_roles(default_role)

        if channel:
            embed = discord.Embed(
                title=f'Bienvenido {member.display_name} a {member.guild.name}',
                description='Por favor lee las reglas.',
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=member.avatar_url_as(size=256))
            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        cmd = ctx.message.content.split()[0]
        embed = discord.Embed(
            title='Error ❌',
            color=discord.Color.red()
        )
        if isinstance(error, commands.CommandNotFound):
            embed.description = f'El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.'
        elif isinstance(error, commands.CheckFailure):
            embed.description = 'No tienes permisos suficientes para usar ese comando.'
        elif isinstance(error, discord.Forbidden):
            embed.description = 'El bot no tiene permisos suficientes para realizar esa acción'
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f'Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.'
        else:
            embed.description = 'Error desconocido'
            guild = crud.get_guid(ctx.guild.id)
            debug = to_bool(crud.get_guild_setting(guild, 'debug'))
            if debug:
                error_msg = str(error)
                if error_msg:
                    embed.description += ':\n\n||```{error_msg}```||'
            logging.error(str(error))
        await ctx.send(embed=embed)


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
        db = session_factory()
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


# TODO Put the help and aliases in the commands here
class BotConfigCmds(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ('manage_guild', True) in ctx.author.permissions_in(ctx.channel)

    @commands.group(help='Configura el bot', invoke_without_command=True)
    async def config(self, ctx):
        # TODO Display a message showing what can be done with this command
        pass

    @config.command()
    async def debug(self, ctx, arg: bool):
        crud.set_guild_setting(ctx.guild.id, 'debug', to_str_bool(arg))
        embed = discord.Embed(
            title='Debug editado! ✅',
            description=f'Debug ha sido puesto como `{arg}`',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @config.command(
        help='Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos separados por un espacio',
        usage='[nuevos prefixes]'
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, *, new_prefixes=None):
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
    async def yt(self, ctx):
        embed = discord.Embed(
            title='Configuración de YT Notifier',
            color=discord.Color.red()
        )
        embed.add_field(
            name='Canal', value=f'Puedes configurar el canal de texto al cual se enviaran las notificaciones usando `{ctx.prefix}config yt set channel #canal`', inline=False)
        embed.add_field(name='Seguir un canal de YouTube',
                        value=f'Para seguir un canal de youtube y recibir notificaciones de sus nuevos videos, usa `{ctx.prefix}config yt add channel <canal>`. Para más información usa `{ctx.prefix}help config yt add channel`\n\nTambién puedes usar `{ctx.prefix}config yt remove playlist <playlist_id>` para eliminar un canal (Puedes ver la id de las playlists más abajo)\n\u200b', inline=False)

        guild = crud.get_guid(ctx.guild.id)
        notifications_channel = crud.get_guild_setting(guild, 'notifications_channel')
        try:
            notifications_channel = int(notifications_channel)
        except TypeError:
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
                value += f'\n- {playlist.playlist_id} (Videos de {channel_title})'
        else:
            value += '\nActualmente no sigues ninguna playlist ni canal'
        embed.add_field(name='Configuraciones Actuales', value=value)
        await ctx.send(embed=embed)

    @yt.group(name='set', invoke_without_command=True)
    async def set_(self, ctx):
        # TODO Display a message showing what can be done with this command
        pass

    @set_.command(help='Coloca el canal al cual se enviaran las novedades (nuevos videos canales de YouTube configurados)')
    async def channel(self, ctx, channel: discord.TextChannel):
        crud.set_guild_setting(ctx.guild.id, 'notifications_channel', str(channel.id))
        embed = discord.Embed(
            title='Canal colocado! ✅',
            description='El canal para las novedades ha sido colocado satisfactoriamente.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @yt.group(invoke_without_command=True)
    async def add(self, ctk):
        # TODO Display a message showing what can be done with this command
        pass

    @add.command(name='channel')
    async def channel_(self, ctx, *, yt_channel):
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
    async def remove(self, ctx):
        # TODO Show a message
        pass

    @remove.command()
    async def playlist(self, ctx, playlist_id):
        guild = crud.get_or_create_guild(ctx.guild.id)
        playlist = crud.get_playlist(playlist_id)
        guild.youtube_playlists.remove(playlist)
        if not playlist.guilds:
            crud.delete_playlist(playlist)

        embed = discord.Embed(
            title='Playlist eliminada! ✅',
            description='La playlist ha sido eliminada correctamente.',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(help='Recarga el bot', usage='[extención]')
    async def reload(self, ctx, *args):
        if args:
            for arg in args:
                self.bot.reload_extension(arg)
        else:
            # TODO Si hay mas extensiones en el futuro hay que agregarlas.
            self.bot.reload_extension('bot.commands')
        embed = discord.Embed(
            title='Reloaded ✅',
            color=discord.Color.red(),
            description='Bot recargado satisfactoriamente!'
        )
        await ctx.send(embed=embed)


# TODO time specific commands, for example: mute user 10seconds
class ModerationCmds(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(help='Elimina los últimos <cantidad> mensajes o el último si ningún argumento es usado.', usage='[cantidad]')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount)
        embed = discord.Embed(
            title='Mensajes eliminados! ✅',
            description=f'{amount} mensajes han sido eliminados satisfactoriamente\nEste mensaje va a ser eliminado en 5 segundos',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed, delete_after=5)

    @commands.command(help='Prohible un usuario en el servidor', usage='<usuario> [razón]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        embed = discord.Embed(
            title=f'Usuario baneado ✅',
            description=f'El usuario {member.name} ha sido baneado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Permite un usuario en el servidor que anteriormente habia sido baneado', usage='<usuario> [razón]')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.Member, *, reason=None):
        await member.unban(reason=reason)
        embed = discord.Embed(
            title=f'Usuario desbaneado ✅',
            description=f'El usuario {member.name} ha sido desbaneado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Expulsa a un usuario del servidor', usage='<usuario> [razón]', aliases=['expulsar'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title=f'Usuario expulsado ✅',
            description=f'El usuario {member.name} ha sido expulsado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Evita que un usuario envie mensajes o entre a canales de voz', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx, member: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        if role is None:
            role = await ctx.guild.create_role(name='Muted', color=discord.Color.dark_grey())
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, send_messages=False, speak=False)
        await member.add_roles(role)
        embed = discord.Embed(
            title=f'Usuario silenciado ✅',
            description=f'El usuario {member.name} ha sido silenciado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Permite a un usuario silenciado hablar y escribir nuevamente', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member, *, reason=None):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        await member.remove_roles(role)
        embed = discord.Embed(
            title=f'Usuario des-silenciado ✅',
            description=f'El usuario {member.name} ha sido des-silenciado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)


class UserCmds(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(help='Muestra ayuda acerca del bot', aliases=['ayuda', 'comandos', 'commands'], usage='[comando]')
    async def help2(self, ctx, command: Optional[commands.Command]):
        if command:
            embed = discord.Embed(
                title=f'Ayuda sobre el comando {command.name}',
                description=f'{command.help}',
                color=discord.Color.red()
            )
            if command.usage:
                embed.description += f'\nUso: `{ctx.prefix}{command.usage}`'
            if command.aliases:
                aliases = '\', \''.join(command.aliases)
                embed.description += f'\nAlias: {aliases}'
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='Ayuda',
                description=f'Prefix: {ctx.prefix}\n\nLista de comandos del bot:',
                color=discord.Color.red()
            )
            for cmd in self.bot.commands:
                value = cmd.help
                if cmd.usage:
                    value += f'\nUso: `{ctx.prefix}{cmd.usage}`'
                if cmd.aliases:
                    aliases = '\', \''.join(cmd.aliases)
                    value += f'\nAlias: {aliases}'

                embed.add_field(name=cmd.name, value=value, inline=False)

            await ctx.send(embed=embed)

    @commands.command(
        help='Muestra el último video subido al canal <canal>' +
        '\n<canal> puede ser la url o el nombre de un canal de youtube', aliases=['ultimo', 'youtube', 'latest'],
        usage='[canal]'
    )
    async def yt(self, ctx, yt_channel):
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
            'part': 'contentDetails',
            'id': channel_id,
            'key': Settings.YOUTUBE_API_KEY
        }
        channel_playlist = (await fetch(self.bot.session, url, params=params))['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        params = {
            'part': 'snippet,contentDetails',
            'maxResults': 1,
            'playlistId': channel_playlist,
            'key': Settings.YOUTUBE_API_KEY
        }
        latest_video = (await fetch(self.bot.session, url, params=params))['items'][0]
        video_url = 'https://www.youtube.com/watch?v=' + latest_video['snippet']['resourceId']['videoId']
        await ctx.send(video_url)

    @commands.command(help='Saluda al usuario que usó el comando o al mencionado', aliases=['hola'], usage='[usuario]')
    async def hello(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        embed = discord.Embed(
            description=f'Hola {member.mention}>',
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(help='Información sobre el servidor')
    async def info(self, ctx: commands.Context):
        embed = discord.Embed(
            title='Información acerca del Servidor',
            color=discord.Color.red()
        )
        guild = ctx.guild  # type: discord.Guild
        embed.add_field(name='Nombre', value=guild.name, inline=False)
        embed.add_field(name='Región', value=guild.region, inline=False)
        if guild.icon_url:
            embed.add_field(name='Ícono', value=guild.icon_url, inline=False)
            embed.set_thumbnail(url=guild.icon_url)
        embed.add_field(name='Dueño', value=guild.owner.mention, inline=False)
        embed.add_field(name='Número de miembros', value=guild.member_count, inline=False)
        embed.add_field(name='(UTC) Creado el día', value=guild.created_at, inline=False)
        await ctx.send(embed=embed)

    @commands.command(help='Muestra la foto de un usuario en un tamaño grande', aliases=['image', 'photo', 'foto', 'imagen'], usage='[usuario]')
    async def avatar(self, ctx, member: Optional[discord.Member]):
        member = member or ctx.author
        embed = discord.Embed(
            title=f'Avatar de {member.display_name}',
            color=discord.Color.red()
        )
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def echo(self, ctx, *, msg):
        await ctx.send(msg)

    @commands.command()
    async def echoembed(self, ctx, *, description):
        embed = discord.Embed(
            title='Echo',
            description=description
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def fullembed(self, ctx, *, description):
        embed = discord.Embed(
            title='Full embed',
            description=description
        )
        embed.set_footer(text='Footer')
        embed.set_thumbnail(url='https://img.icons8.com/bubbles/2x/google-logo.png')
        embed.set_image(url='https://d2dgtayfmpkokn.cloudfront.net/wp-content/uploads/sites/322/2016/09/11074109/google-icon.jpg')
        embed.set_author(name='Author')
        embed.add_field(name='Field', value='Value')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Listeners(bot))
    bot.add_cog(Loops(bot))
    bot.add_cog(BotConfigCmds(bot))
    bot.add_cog(ModerationCmds(bot))
    bot.add_cog(UserCmds(bot))
