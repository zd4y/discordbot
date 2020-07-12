import discord
from discord.ext import commands

from ..bot import Bot
from .. import crud
from ..utils import update_message, display_roles


class Verification(commands.Cog, name='Configura la verificacion'):
    def __init__(self, bot: Bot):
        self.bot = bot

    def cog_check(self, ctx: commands.Context):
        return ('manage_guild', True) in ctx.author.permissions_in(ctx.channel)

    @commands.group()
    async def verification(self, ctx: commands.Context):
        pass

    @verification.command()
    async def settext(self, ctx: commands.Context, *, value: str):
        crud.set_guild_setting(ctx.guild.id, 'verification_message_text', value)

        embed = discord.Embed(
            title='Texto colocado',
            description='El mensaje se actualizará en breve.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        await update_message(self.bot, ctx)

    @verification.command()
    async def addrole(self, ctx: commands.Context, role: discord.Role, emoji: str):
        crud.add_verification_role(ctx.guild.id, role.id, emoji=emoji)

        # TODO !!!!
        for guild_channel in ctx.guild.channels:
            await guild_channel.set_permissions(role, read_messages=True)

        embed = discord.Embed(
            title='Rol agregado',
            description='El mensaje se actualizará en breve.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        await update_message(self.bot, ctx)

    # TODO !!!!
    @verification.command()
    async def disable(self, ctx: commands.Context):
        crud.set_guild_setting(ctx.guild.id, 'verification_message', '')
        crud.set_guild_setting(ctx.guild.id, 'verification_channel', '')
        everyone = ctx.guild.default_role
        for guild_channel in ctx.guild.channels:
            await guild_channel.set_permissions(everyone, read_messages=True)

    # TODO !!!
    @verification.command()
    async def enable(self, ctx: commands.Context):
        everyone = ctx.guild.default_role
        guild = crud.get_guild(ctx.guild.id)
        channel_id = crud.get_guild_setting(guild, 'verification_channel')

        for guild_channel in ctx.guild.channels:
            overwrite = discord.PermissionOverwrite()
            overwrite.update(read_messages=False)

            if channel_id.isdigit() and guild_channel.id == int(channel_id):
                overwrite.update(read_messages=True)

            await guild_channel.set_permissions(everyone, overwrite=overwrite)

        await update_message(self.bot, ctx)

    @verification.command()
    async def update(self, ctx: commands.Context):
        embed = discord.Embed(
            title='Actualizando mensaje',
            description='El mensaje se actualizará en breve.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        await update_message(self.bot, ctx)

    @verification.command()
    async def info(self, ctx: commands.Context):
        roles = crud.get_verification_roles(ctx.guild.id)
        description = 'No has configurado ningún rol.'
        if roles:
            description = await display_roles(ctx, roles, include_id=True)

        description += f'\nPuedes agregar roles usando `{ctx.prefix}verification addrole <rol> <emoji>`'
        description += f'\nTambién puedes eliminar roles usando `{ctx.prefix}verification removerole <id>`'

        embed = discord.Embed(
            title='Roles de verificación actuales',
            description=description,
            color=discord.Color.red()
        )

        await ctx.send(embed=embed)

    @verification.command()
    async def removerole(self, ctx: commands.Context, role_id: int):
        crud.remove_verification_role(role_id)

        embed = discord.Embed(
            title='Rol eliminado',
            description='El mensaje se actualizará en breve.',
            color=discord.Color.green()
        )

        await ctx.send(embed=embed)
        await update_message(self.bot, ctx)
