import discord
from discord.ext import commands

from .. import crud
from ..bot import Bot
from ..utils import callback as cb


no_logs_channel_msg = 'Usuario {title}. Considere agregar un canal para los logs usando `{prefix}setchannel ' \
                      'moderation #canal`. Este mensaje se eliminara en 10 segundos.'

usage = '<usuario> [duración (minutos)] [razón]'


class UnModerationCmds(commands.Cog, name='Revocar moderación'):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def unmoderate(
            self, ctx: commands.Context, callback: callable, title: str, reason: str, member: discord.Member
    ):
        await ctx.message.delete()
        await callback(reason=reason)

        guild = crud.get_guid(member.guild.id)
        channel = crud.get_channel_setting(self.bot, guild, 'moderation_logs_channel')
        moderation = crud.get_moderation(title, member.id, ctx.guild.id)
        crud.revoke_moderation(moderation)

        if channel:
            embed = discord.Embed(
                title=f'Usuario {title}',
                description=f'El usuario {member.mention} ha sido {title} por {ctx.author.mention}',
                color=discord.Color.green()
            )

            if reason:
                embed.description += f'\n**Razón**: {reason}'

            await channel.send(embed=embed)

        else:
            await ctx.send(no_logs_channel_msg.format(title=title, prefix=ctx.prefix), delete_after=10)

    @commands.command(help='Permite un usuario en el servidor que anteriormente habia sido baneado', usage='<usuario> [razón]')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
        await self.unmoderate(ctx, member.unban, 'desbaneado', reason, member)

    @commands.command(help='Permite a un usuario silenciado hablar y escribir nuevamente', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
        role = discord.utils.get(ctx.guild.roles, name='Muted')
        await self.unmoderate(ctx, cb(member.remove_roles, role), 'des-silenciado', reason, member)
