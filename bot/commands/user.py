import re
import discord

from ..bot import Bot
from ..utils import fetch
from typing import Optional
from ..config import Settings
from discord.ext import commands


class UserCmds(commands.Cog, name='Comandos para el usuario'):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(help='Muestra ayuda acerca del bot', aliases=['ayuda', 'comandos', 'commands'], usage='[comando]')
    async def help(self, ctx: commands.Context, *, command_name: str = ''):
        no_description_msg = '(Sin descripción)'

        def display_info(cmd: commands.Command, simple=False):
            command_description = ''

            if simple:
                command_description += f'`{cmd.name}`: '
                command_description += cmd.help or no_description_msg
                command_description += '\n'
                return command_description

            if cmd.usage:
                command_description += f'\nUso: `{ctx.prefix}{cmd.name} {cmd.usage}`'

            if cmd.aliases:
                aliases_list = "`, `".join(cmd.aliases)
                command_description = f'\nAlias: `{aliases_list}`'

            group_commands = getattr(cmd, 'commands', None)

            if group_commands:
                command_description += '\n\n**Commands:**\n'
                for group_command in group_commands:
                    command_description += display_info(group_command, simple=True)

            return command_description

        if command_name:
            command = self.bot.get_command(command_name)
            if command is None:
                embed = discord.Embed(
                    title=f'El comando {command_name} no existe',
                    description=f'Usa `{ctx.prefix}help` para obtener una lista sobre los comandos.',
                    color=discord.Color.red()
                )
            else:
                embed = discord.Embed(
                    title=f'Ayuda sobre el comando {command.name}',
                    description=command.help or no_description_msg,
                    color=discord.Color.red()
                )
                embed.description += display_info(command)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title='Ayuda',
                description=f'Prefix: `{ctx.prefix}`',
                color=discord.Color.red()
            )

            embed.description += f'\nUsa `{ctx.prefix}{ctx.command} <comando>` para obtener más información sobre un comando específico.'
            embed.description += '\nLista de comandos del bot:'

            for cog_name, cog in self.bot.cogs.items():
                cog_commands = cog.get_commands()
                if not cog_commands:
                    continue

                value = ''
                for command in cog_commands:
                    value += display_info(command, simple=True)
                embed.add_field(name=cog.qualified_name or cog_name, value=value, inline=False)

            await ctx.send(embed=embed)

    @commands.command(
        help='Muestra el último video subido al canal <canal>' +
        '\n<canal> puede ser la url o el nombre de un canal de youtube', aliases=['ultimo', 'youtube', 'latest'],
        usage='[canal]'
    )
    async def yt(self, ctx: commands.Context, yt_channel: str):
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
    async def hello(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        member = member or ctx.author
        embed = discord.Embed(
            description=f'Hola {member.mention}',
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
    async def avatar(self, ctx: commands.Context, member: Optional[discord.Member] = None):
        member = member or ctx.author
        embed = discord.Embed(
            title=f'Avatar de {member.display_name}',
            color=discord.Color.red()
        )
        embed.set_image(url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command()
    async def echo(self, ctx: commands.Context, *, msg: str):
        await ctx.send(msg)

    @commands.command()
    async def echoembed(self, ctx: commands.Context, *, description: str):
        embed = discord.Embed(
            title='Echo',
            description=description
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def fullembed(self, ctx: commands.Context, *, description: str):
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
