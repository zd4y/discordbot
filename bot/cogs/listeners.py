import logging
from datetime import datetime
from asyncio import create_task

import discord
from discord.ext import commands

from .. import crud
from ..bot import Bot
from ..utils import to_bool
from ..config import Settings
from ..models import Moderation


async def unban(_: discord.Guild, member: discord.Member, reason: str):
    await member.unban(reason=reason)


async def unmute(guild: discord.Guild, member: discord.Member, _: str):
    role = discord.utils.get(guild.roles, name='Muted')
    await member.remove_roles(role)


async def revoke_moderation(guild: discord.Guild, moderation: Moderation):
    if moderation.expiration_date > datetime.utcnow():
        await discord.utils.sleep_until(moderation.expiration_date)

    map_moderations = {
        'silenciado': unmute,
        'baneado': unban
    }

    func = map_moderations.get(moderation.type)
    member = guild.get_member(moderation.user_id)
    await func(guild, member, moderation.reason)
    crud.revoke_moderation(moderation)


class Listeners(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        activity = discord.Game('prefix: ' + Settings.DEFAULT_SETTINGS['prefix'])
        await self.bot.change_presence(activity=activity)
        logging.info('Bot is ready')

        for guild in self.bot.guilds:
            moderations = crud.get_all_moderations(guild.id, revoked=False)
            for moderation in moderations:
                create_task(revoke_moderation(guild, moderation))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        cmd = ctx.message.content.split()[0]
        embed = discord.Embed(
            title='Error ❌',
            color=discord.Color.red()
        )

        original = getattr(error, 'original', None)

        unknown_error_msg = 'Error desconocido'
        forbidden_message = 'El bot no tiene permisos suficientes para realizar esa acción. ||' + \
                            getattr(original, 'text', '') + '||'
        no_permission_msg = 'No tienes permisos suficientes para usar ese comando.'

        errors = {
            commands.ExpectedClosingQuoteError: 'Te ha faltado cerrar una comilla.',
            commands.BadArgument: 'Has puesto mal algún argumento.',
            commands.CommandError: 'No tienes acceso a este comando.',
            commands.CommandNotFound: f'El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.',
            commands.CheckFailure: no_permission_msg,
            commands.MissingPermissions: no_permission_msg,
            commands.MissingRequiredArgument: f'Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.',
            commands.BotMissingPermissions: forbidden_message
        }

        original_errors = {
            discord.Forbidden: forbidden_message
        }

        original_type = type(original)
        message = errors.get(type(error), original_errors.get(original_type))

        embed.description = message

        if message is None:
            embed.description = unknown_error_msg
            guild = crud.get_guild(ctx.guild.id)
            debug = to_bool(crud.get_guild_setting(guild, 'debug'))
            if debug:
                error_msg = str(error)
                if error_msg:
                    embed.description += f':\n||```{error_msg}```||'
            logging.error(str(error), type(error), getattr(original, 'text', ''))

        await ctx.send(embed=embed, delete_after=10)

    @staticmethod
    def is_verification_message(payload):
        guild = crud.get_guild(payload.guild_id)
        message_id = crud.get_guild_setting(guild, 'verification_message')

        if not message_id:
            return False

        return int(message_id) == payload.message_id


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not self.is_verification_message(payload):
            return

        member = payload.member

        if member.bot:
            return

        db_role = crud.get_role_by_emoji(payload.guild_id, str(payload.emoji))
        role = discord.utils.get(member.guild.roles, id=db_role.role_id) if db_role else None

        if role:
            await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not self.is_verification_message(payload):
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member.bot:
            return

        db_role = crud.get_role_by_emoji(guild.id, str(payload.emoji))
        role = discord.utils.get(guild.roles, id=db_role.role_id) if db_role else None

        if role:
            await member.remove_roles(role)
