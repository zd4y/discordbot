import discord
from discord.ext import commands
from datetime import datetime, timedelta

from .. import crud
from ..bot import Bot
from ..models import Moderation
from ..utils import callback as cb


no_logs_channel_msg = 'Usuario {title}. Considere agregar un canal para los logs usando `{prefix}setchannel ' \
                      'moderation #canal`. Este mensaje se eliminara en 10 segundos.'

usage = '<usuario> [duración (minutos)] [razón]'


class ModerationCmds(commands.Cog, name='Moderación'):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def moderate(
            self,
            ctx: commands.Context,
            callback: callable,
            title: str,
            args: str,
            member: discord.Member,
            after_duration: callable = None
    ):
        if not ctx.author.top_role > member.top_role:
            return await ctx.send('No puedes moderar a este usuario.')

        args = args.split()
        if len(args) > 1:
            duration, *reason = args
            reason = ' '.join(reason)

            if duration.replace('.', '', 1).isdigit():
                duration = float(duration)
            else:
                reason = duration + ' ' + reason
                duration = 0
        elif len(args) == 1:
            reason = args[0]
            duration = None
        else:
            reason = None
            duration = None

        await ctx.message.delete()
        moderation_date = datetime.utcnow()

        expiration_date = None
        if duration and after_duration:
            expiration_date = moderation_date + timedelta(minutes=duration)

        crud.moderate(title, member.id, moderation_date, expiration_date, ctx.guild.id, ctx.author.id, reason or '')

        await callback(reason=reason)

        guild = crud.get_guid(member.guild.id)
        channel = crud.get_channel_setting(self.bot, guild, 'moderation_logs_channel')

        dm = member.dm_channel
        if dm is None:
            dm = await member.create_dm()

        try:
            await dm.send(f'Has sido {title} en {ctx.guild.name}. Recuerda seguir las reglas!')
        except discord.Forbidden:
            await ctx.send('El usuario tiene bloqueados los mensajes directos', delete_after=10)

        if channel:
            embed = discord.Embed(
                title=f'Usuario {title}',
                description=f'El usuario {member.mention} ha sido {title} por {ctx.author.mention}',
                color=discord.Color.green()
            )

            if reason:
                embed.description += f'\n**Razón**: {reason}'

            if expiration_date:
                embed.description += f'\n**Duración**: {duration} minutos'

            message = member.mention
            rules_channel = crud.get_channel_setting(self.bot, guild, 'rules_channel')

            if rules_channel:
                value = 'Lee las reglas: ' + rules_channel.mention
                embed.description += '\n' + value
                message += ' ' + value

            await channel.send(message, embed=embed)

        else:
            await ctx.send(no_logs_channel_msg.format(title=title, prefix=ctx.prefix), delete_after=10)

        if expiration_date:
            await discord.utils.sleep_until(expiration_date)
            moderation = crud.get_moderation(title, member.id, ctx.guild.id)

            if moderation.expired:
                await after_duration(reason=reason)
                crud.revoke_moderation(moderation)

    @commands.command(help='Advierte a un usuario.', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
        role = discord.utils.get(ctx.guild.roles, name='Warning')

        if role is None:
            role = await ctx.guild.create_role(name='Warning', color=discord.Color.darker_grey())

        await self.moderate(ctx, cb(member.add_roles, role), 'advertido', reason, member)

    def show_history(self, moderation: Moderation, embed: discord.Embed, include_type=True):
        embed.description += '\n'

        for index, moderation in enumerate(moderation):
            embed.description += f'\n`{index + 1}` '

            if include_type:
                embed.description += f'[{moderation.type.title()}] '

            reason = moderation.reason or 'Sin razón'
            embed.description += f'**{reason}** '

            moderator_id = moderation.moderator_id
            moderator = None

            if moderator_id:
                channel: discord.TextChannel
                moderator = discord.utils.get(self.bot.users, id=int(moderator_id))

            if moderator:
                embed.description += f'por {moderator.mention}'

            embed.description += 'en `' + moderation.creation_date.strftime('%a %d, %Y') + '`'

    @commands.command()
    async def history(self, ctx: commands.Context, member: discord.Member):
        history = crud.get_all_moderations(ctx.guild.id, member.id)

        embed = discord.Embed(
            title=f'Historial de moderación',
            description=f'Historial de {member.mention}. Total: {len(history)}',
            color=discord.Color.red()
        )

        self.show_history(history, embed)
        await ctx.send(embed=embed)

    @commands.command()
    async def warninfo(self, ctx: commands.Context, member: discord.Member):
        warnings = crud.get_moderations('advertido', member.id, ctx.guild.id)

        embed = discord.Embed(
            title=f'Historial de warnings',
            description=f'Warnings de {member.mention}. Total: {len(warnings)}',
            color=discord.Color.red()
        )

        self.show_history(warnings, embed, include_type=False)
        await ctx.send(embed=embed)

    @commands.command(help='Elimina los últimos <cantidad> mensajes o el último si ningún argumento es usado.', usage='[cantidad]')
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, amount: int = 1):
        await ctx.channel.purge(limit=amount+1)

        embed = discord.Embed(
            title='Mensajes eliminados! ✅',
            description=f'{amount} mensajes han sido eliminados satisfactoriamente\nEste mensaje va a ser eliminado en 5 segundos',
            color=discord.Color.red()
        )

        await ctx.send(embed=embed, delete_after=5)

    @commands.command(help='Prohibe un usuario en el servidor', usage=usage)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, args: str = ''):
        await self.moderate(ctx, member.ban, 'baneado', args, member, member.unban)

    @commands.command(help='Expulsa a un usuario del servidor', usage='<usuario> [razón]', aliases=['expulsar'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, args: str = ''):
        await self.moderate(ctx, member.kick, 'expulsado', args, member)

    @commands.command(help='Evita que un usuario envie mensajes o entre a canales de voz', usage=usage)
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, *, args: str = ''):
        role = discord.utils.get(ctx.guild.roles, name='Muted')

        if role is None:
            role = await ctx.guild.create_role(name='Muted', color=discord.Color.dark_grey())

            overwrite = discord.PermissionOverwrite(send_messages=False, speak=False)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role, overwrite=overwrite)

        await self.moderate(ctx, cb(member.add_roles, role), 'silenciado', args, member, cb(member.remove_roles, role))
