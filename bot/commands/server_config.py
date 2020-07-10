import discord
from discord.ext import commands

from ..bot import Bot
from .. import crud, youtube
from ..utils import is_url, get_verification_message

settings = {
    'moderation': 'moderation_logs_channel',
    'youtube': 'notifications_channel',
    'rules': 'rules_channel',
    'verification': 'verification_channel'
}


# TODO Put the help and aliases in the commands here
class ServerConfigCmds(commands.Cog, name='Configuraciones del bot para el servidor'):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return ('manage_guild', True) in ctx.author.permissions_in(ctx.channel)

    @commands.command(help='...', invoke_without_command=True)
    async def setchannel(self, ctx: commands.Context, setting, channel: discord.TextChannel):
        if setting not in settings:
            return

        if setting == 'verification':
            embed = discord.Embed(
                title='Verificación',
                description='Aún no has configurado el sistema de verificación.',
                color=discord.Color.green()
            )

            cmd = f'{ctx.prefix}verification '
            embed.description += f'\nColoca un mensaje al inicio usando `{cmd}settext <texto>`' \
                                 f'\nAgrega roles usando `{cmd}addrole <rol> <emoji>`' \
                                 f'\nElimina roles usando `{cmd}removerole <id del rol>`' \
                                 f'\nPuedes ver las ids de los roles usando `{cmd}info`' \
                                 '\nEl emoji debe tenerlo disponible el bot' \
                                 f'\nUna vez lo hayas configurado usa `{cmd}enable` para ' \
                                 'activar el sistema de verificación' \
                                 f'\nSi ya lo configuraste y quieres actualizar este mensaje usa `{cmd}update`'

            message = await channel.send(embed=embed)

            crud.set_guild_setting(ctx.guild.id, 'verification_message', message.id)
            crud.set_guild_setting(ctx.guild.id, 'verification_channel', message.channel.id)
        else:
            crud.set_guild_setting(ctx.guild.id, settings[setting], str(channel.id))

        embed = discord.Embed(
            title='Canal colocado! ✅',
            description='El canal ha sido colocado.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)

    @commands.group(help='Coloca canales y configuraciones. Canales para colocar: ' + ' '.join(settings.keys()))
    async def set(self, ctx: commands.Context):
        pass

    @set.command(
        help='Muestra el prefix del bot o lo cambia, puedes cambiarlo a múltiples prefixes pasando varios argumentos '
             'separados por un espacio',
        usage='[nuevos prefixes separados por un espacio]'
    )
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx: commands.Context, *, new_prefixes: str = ''):
        def format_prefixes(p):
            p = p.split()
            return '`' + '`, `'.join(p) + '`'

        if new_prefixes:
            crud.set_guild_setting(ctx.guild.id, 'prefix', new_prefixes)
            embed = discord.Embed(
                title='Prefix editado! ✅',
                description=f'Los prefixes ahora son: {format_prefixes(new_prefixes)}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
        else:
            guild = crud.get_guid(ctx.guild.id)
            prefixes = crud.get_guild_setting(guild, 'prefix')
            embed = discord.Embed(
                title='Prefix del Bot',
                description=f'Los prefixes actuales son: {format_prefixes(prefixes)}',
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(help='Información sobre las noticiaciones de youtube')
    async def ytinfo(self, ctx: commands.Context):
        embed = discord.Embed(
            title='Configuración de YT Notifier',
            color=discord.Color.red()
        )

        embed.add_field(
            name='Canal', value=f'Puedes configurar el canal de texto al cual se enviaran las notificaciones usando '
                                f'`{ctx.prefix}set ytlogchannel #canal`', inline=False)

        value = "Para seguir un canal de youtube y recibir notificaciones de sus nuevos videos, usa " \
                f"`{ctx.prefix}add ytchannel <nombre del canal o url>`\n\nTambién puedes usar `{ctx.prefix}remove " \
                f"ytchannel <id>` para eliminar un canal (Puedes ver la id de las playlists más abajo)\n\u200b"

        embed.add_field(name='Seguir un canal de YouTube',
                        value=value, inline=False)

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
            value += '\nLa id de los canales seguidos son:'
            for playlist in followed_playlists:
                channel_title = playlist.channel
                if channel_title is None:
                    videos = await youtube.get_playlist_videos(self.bot.session, playlist.playlist_id, max_results=1)
                    channel_title = videos[0]['snippet']['channelTitle']
                value += f'\n`{playlist.id}`: Videos de {channel_title}'
        else:
            value += '\nActualmente no sigues ningun canal'
        embed.add_field(name='Configuraciones Actuales', value=value)
        await ctx.send(embed=embed)

    @commands.group(help='')
    async def add(self, ctx: commands.Context):
        pass

    @add.command()
    async def ytchannel(self, ctx: commands.Context, *, yt_channel: str):
        if is_url(yt_channel):
            channel_id = yt_channel.split('/')[-1]
        else:
            channel_id = await youtube.search_channel(self.bot.session, yt_channel)

        channel = await youtube.fetch_channel(self.bot.session, channel_id, snippet=True)
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

    @commands.group(help='')
    async def remove(self, ctx: commands.Context):
        pass

    # TODO: Use an integer instead of the playlist_id
    @remove.command(name='ytchannel')
    async def remove_ytchannel(self, ctx: commands.Context, num: int):
        guild = crud.get_or_create_guild(ctx.guild.id)
        playlist = crud.get_playlist(db_id=num)
        guild.youtube_playlists.remove(playlist)
        if not playlist.guilds:
            crud.delete_playlist(playlist)

        embed = discord.Embed(
            title='Canal eliminado! ✅',
            description='El canal ha sido eliminado correctamente.',
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @remove.command()
    async def channel(self, ctx: commands.Context, name: str):
        if name not in settings:
            return

        if name == 'verification':
            guild = crud.get_guid(ctx.guild.id)
            message = await get_verification_message(self.bot, guild)
            await message.delete()
            crud.set_guild_setting(ctx.guild.id, 'verification_message', '')

        crud.set_guild_setting(ctx.guild.id, settings[name], '')

        embed = discord.Embed(
            title='Configuración eliminada! ✅',
            description='La configuración ha sido eliminada correctamente.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
