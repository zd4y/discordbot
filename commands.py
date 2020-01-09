import discord
from discord.ext import commands, tasks
from typing import Optional
import requests
from config import Config, ServerConfig, YoutubeVideos
import re


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game('prefix: !')
        await self.bot.change_presence(activity=activity)
        print('Bot is ready')

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
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
            # TODO See if server has debug=True, if so, show the error. Else:
            embed.description = 'Error desconocido'
            # TODO Log the error
            print(error, error.__class__)
        await ctx.send(embed=embed)


# TODO a lot to do here :C
class Loops(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.youtube_notifier.start()

    def cog_unload(self):
        self.youtube_notifier.cancel()

    @tasks.loop(minutes=5)
    async def youtube_notifier(self):
        print()
        print()
        print('INFO: starting yt notifier')
        for guild in self.bot.guilds:
            print(f'INFO: - starting with guild {guild.name}')
            channel_id = ServerConfig.get_setting(guild.id, 'notifications_channel')
            channel = discord.utils.get(guild.channels, id=channel_id)
            print(f'INFO: -- channel is {channel}')
            if channel is None:
                continue
            followed_playlists = ServerConfig.get_setting(guild.id, 'followed_playlists')
            print(f'INFO: -- followed playlists are {followed_playlists}')
            if followed_playlists is None:
                continue
            for playlist_id in followed_playlists:
                print(f'INFO --- starting with playlist_id: {playlist_id}')
                URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
                params = {
                    'part': 'snippet,contentDetails',
                    'maxResults': 5,
                    'playlistId': playlist_id,
                    'key': Config.YOUTUBE_API_KEY
                }
                res = requests.get(URL, params=params)
                videos = res.json()['items'][::-1]
                print(f'INFO: --- got {len(videos)} videos')
                for video in videos:
                    print(f'INFO: --- checking the cache for the video: {video}')
                    print()
                    video_cache = YoutubeVideos.get_videos()
                    video_info = video['snippet']
                    video_id = video_info['resourceId']['videoId']
                    if video_id in video_cache:
                        print('INFO: ---- video was in cache, skipping')
                        continue
                    print('INFO: ---- video was not in cache! sending message to the channel')
                    video_url = 'https://www.youtube.com/watch?v=' + video_info['resourceId']['videoId']
                    video_desc = video_info['description'][:151] + '...'
                    embed = discord.Embed(
                        title=video_info['title'],
                        description=video_desc,
                        url=video_url,
                        color=discord.Color.red()
                    )
                    embed.description += f'\n{video_url}'
                    embed.set_image(url=video_info['thumbnails']['medium']['url'])
                    await channel.send(embed=embed)
                    print('INFO: ---- message sent')
                    YoutubeVideos.add_videos(playlist_id, [video_id])
                    print()
            print()
            print()


# TODO Put the help and aliases in the commands here
# TODO Config debug true/false command
class BotConfigCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def cog_check(self, ctx):
        return ('manage_guild', True) in ctx.author.permissions_in(ctx.channel)

    @commands.group(help='Configura el bot', invoke_without_command=True)
    async def config(self, ctx):
        # TODO Display a message showing what can be done with this command
        pass

    @config.command(
        help='Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos separados por un espacio',
        usage='[nuevos prefixes]'
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, *args):
        if args:
            ServerConfig.set_setting(ctx.guild.id, 'prefix', ' '.join(args))
            prefixes = ' '.join(args)
            embed = discord.Embed(
                title='Prefix editado! ✅',
                description=f'Los prefixes ahora son: {prefixes}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            prefixes = self.bot.command_prefix(self.bot, ctx.message)
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

        notifications_channel = ServerConfig.get_setting(ctx.guild.id, 'notifications_channel')
        try:
            notifications_channel = discord.utils.get(ctx.guild.channels, id=int(notifications_channel)).mention
        except Exception:
            notifications_channel = 'Ninguno/Eliminado'
        value = f'El canal para notificaciones es: {notifications_channel}'
        followed_playlists = ServerConfig.get_setting(ctx.guild.id, 'followed_playlists')
        if followed_playlists:
            followed_playlists = followed_playlists.split()
            value += '\nLa id de las playlists seguidas son:'
            for playlist_id in followed_playlists:
                URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
                params = {
                    'part': 'snippet',
                    'maxResults': '1',
                    'playlistId': playlist_id,
                    'key': Config.YOUTUBE_API_KEY
                }
                res = requests.get(URL, params=params)
                channel_title = res.json()['items'][0]['snippet']['channelTitle']
                value += f'\n- {playlist_id} (Videos de {channel_title})'
        else:
            value += '\nActualmente no sigues ninguna playlist ni canal'
        embed.add_field(name='Configuraciones Actuales', value=value)
        await ctx.send(embed=embed)

    @yt.group(name='set', invoke_without_command=True)
    async def set_(self, ctx):
        # TODO Display a message showing what can be done with this command
        pass

    @set_.command(help='Coloca el canal al cual se enviaran las novedades (nuevos videos canal de YouTube, Absolute)')
    async def channel(self, ctx, channel: discord.TextChannel):
        ServerConfig.set_setting(ctx.guild.id, 'notifications_channel', channel.id)
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
    async def channel_(self, ctx, yt_channel):
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        is_url = bool(pattern.search(yt_channel))
        if is_url:
            channel_id = yt_channel.split('/')[-1]
        else:
            URL = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'type': 'channel',
                'maxResults': 1,
                'q': yt_channel,
                'key': Config.YOUTUBE_API_KEY
            }
            res = requests.get(URL, params=params)
            channel_id = res.json()['items'][0]['snippet']['channelId']

        URL = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'snippet,contentDetails',
            'id': channel_id,
            'key': Config.YOUTUBE_API_KEY
        }
        res = requests.get(URL, params=params)
        channel = res.json()['items'][0]
        channel_playlist = channel['contentDetails']['relatedPlaylists']['uploads']
        followed_playlists = ServerConfig.get_setting(ctx.guild.id, 'followed_playlists')
        if followed_playlists:
            followed_playlists = followed_playlists.split()
        else:
            followed_playlists = []
        followed_playlists.append(channel_playlist)
        ServerConfig.set_setting(ctx.guild.id, 'followed_playlists', ' '.join(followed_playlists))

        channel_info = channel['snippet']
        channel_title = channel_info['title']
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
        followed_playlists = ServerConfig.get_setting(ctx.guild.id, 'followed_playlists')
        if followed_playlists:
            followed_playlists = followed_playlists.split()
        else:
            followed_playlists = []
        followed_playlists.remove(playlist_id)
        ServerConfig.set_setting(ctx.guild.id, 'followed_playlists', ' '.join(followed_playlists))
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
            self.bot.reload_extension('commands')
        embed = discord.Embed(
            title='Reloaded ✅',
            color=discord.Color.red(),
            description='Bot recargado satisfactoriamente!'
        )
        await ctx.send(embed=embed)


class ModerationCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
    async def ban(self, ctx, member: discord.Member, *args: str):
        reason = ' '.join(args) or None
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
    async def unban(self, ctx, member: discord.Member, *args: str):
        reason = ' '.join(args) or None
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
    async def kick(self, ctx, member: discord.Member, *args: str):
        reason = ' '.join(args) or None
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
    async def mute(self, ctx, member: discord.Member, *args):
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
        reason = ' '.join(args)
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Permite a un usuario silenciado hablar y escribir nuevamente', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx, member: discord.Member, *args):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        await member.remove_roles(role)
        embed = discord.Embed(
            title=f'Usuario des-silenciado ✅',
            description=f'El usuario {member.name} ha sido des-silenciado satisfactoriamente',
            color=discord.Color.red()
        )
        reason = ' '.join(args)
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)


class UserCmds(commands.Cog):
    def __init__(self, bot: commands.Bot):
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
            # TODO Remove this print
            print(command.args)
            await ctx.send(embed=embed)
        else:
            # TODO Get all prefixes from database (not existing yet)
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
        help='Muestra el último video subido al canal <canal> o al de Absolute si ningun argumento es pasado.' +
        '\n<canal> puede ser la url o el nombre de un canal de youtube', aliases=['ultimo', 'youtube', 'latest'],
        usage='[canal]'
    )
    async def yt(self, ctx, yt_channel=None):
        if yt_channel is None:
            yt_channel = 'https://www.youtube.com/channel/UCvnoM0R1sDKm-YCPifEso_g'  # Canal de Absolute
        pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        is_url = bool(pattern.search(yt_channel))
        if is_url:
            channel_id = yt_channel.split('/')[-1]
        else:
            URL = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'type': 'channel',
                'maxResults': 1,
                'q': yt_channel,
                'key': Config.YOUTUBE_API_KEY
            }
            res = requests.get(URL, params=params)
            channel_id = res.json()['items'][0]['snippet']['channelId']

        URL = 'https://www.googleapis.com/youtube/v3/channels'
        params = {
            'part': 'contentDetails',
            'id': channel_id,
            'key': Config.YOUTUBE_API_KEY
        }
        res = requests.get(URL, params=params)
        channel_playlist = res.json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        URL = 'https://www.googleapis.com/youtube/v3/playlistItems'
        params = {
            'part': 'snippet,contentDetails',
            'maxResults': 1,
            'playlistId': channel_playlist,
            'key': Config.YOUTUBE_API_KEY
        }
        res = requests.get(URL, params=params)
        latest_video = res.json()['items'][0]
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


def setup(bot: commands.Bot):
    bot.add_cog(Listeners(bot))
    bot.add_cog(Loops(bot))
    bot.add_cog(BotConfigCmds(bot))
    bot.add_cog(ModerationCmds(bot))
    bot.add_cog(UserCmds(bot))
