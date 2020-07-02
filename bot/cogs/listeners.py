import logging
import discord
from discord.ext import commands

from .. import crud
from ..bot import Bot
from ..utils import to_bool


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
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        cmd = ctx.message.content.split()[0]
        embed = discord.Embed(
            title='Error ❌',
            color=discord.Color.red()
        )

        forbidden_message = 'El bot no tiene permisos suficientes para realizar esa acción.'

        unknown_error_msg = 'Error desconocido'

        errors = {
            commands.CommandError: 'No tienes acceso a este comando.',
            commands.CommandNotFound: f'El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.',
            commands.CheckFailure: 'No tienes permisos suficientes para usar ese comando.',
            commands.MissingRequiredArgument: f'Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.',
            commands.BotMissingPermissions: forbidden_message
        }

        original_errors = {
            discord.Forbidden: forbidden_message
        }

        original_type = type(getattr(error, 'original', None))

        message = errors.get(type(error), original_errors.get(original_type))

        embed.description = message

        if message is None:
            embed.description = unknown_error_msg
            guild = crud.get_guid(ctx.guild.id)
            debug = to_bool(crud.get_guild_setting(guild, 'debug'))
            if debug:
                error_msg = str(error)
                if error_msg:
                    embed.description += ':\n\n||```{error_msg}```||'
            logging.error(str(error))

        await ctx.send(embed=embed)
