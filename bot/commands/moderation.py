import re
import asyncio
import discord

from ..bot import Bot
from discord.ext import commands


# TODO time specific commands, for example: mute user 10seconds
class ModerationCmds(commands.Cog, name='Moderación'):
    def __init__(self, bot: Bot):
        self.bot = bot

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

    @commands.command(help='Prohibe un usuario en el servidor', usage='<usuario> [razón]')
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
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
    async def unban(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
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
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
        await member.kick(reason=reason)
        embed = discord.Embed(
            title=f'Usuario expulsado ✅',
            description=f'El usuario {member.name} ha sido expulsado satisfactoriamente',
            color=discord.Color.red()
        )
        if reason:
            embed.description += f'\nRazón: {reason}'
        await ctx.send(embed=embed)

    @commands.command(help='Evita que un usuario envie mensajes o entre a canales de voz', usage='<usuario> <duración (minutos)> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: int = 0, *, reason: str = ''):
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

        if duration:
            await asyncio.sleep(duration*60)
            await member.remove_roles(role)

    @commands.command(help='Permite a un usuario silenciado hablar y escribir nuevamente', usage='<usuario> [razón]')
    @commands.has_permissions(manage_messages=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member, *, reason: str = ''):
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
