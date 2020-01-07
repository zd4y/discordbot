from discord.ext.commands import command, has_permissions
from discord import Embed, Member, Color, utils
from typing import Optional


@command(help='Saluda al usuario que usó el comando o al mencionado', aliases=['hola'], usage='hello [<usuario>]')
async def hello(ctx, member: Optional[Member]):
    member = member or ctx.author
    embed = Embed(
        description=f'Hola <@!{member.id}>',
        color=Color.red()
    )
    await ctx.send(embed=embed)


@command(help='Elimina los ultimos <cantidad> mensajes o el último si ningún argumento es usado.', usage='clear [<cantidad>]')
@has_permissions(manage_messages=True)
async def clear(ctx, amount=1):
    await ctx.channel.purge(limit=amount)
    embed = Embed(
        title='Mensajes eliminados! ✅',
        description=f'{amount} mensajes han sido eliminados satisfactoriamente',
        color=Color.red()
    )
    await ctx.send(embed=embed)


@command(help='Información sobre el servidor', usage='info')
async def info(ctx):
    embed = Embed(
        title='Información acerca del Servidor',
        color=Color.red()
    )
    guild = ctx.guild
    embed.add_field(name='Nombre', value=guild.name, inline=False)
    embed.add_field(name='Región', value=guild.region, inline=False)
    if guild.icon_url:
        embed.add_field(name='Ícono', value=guild.icon_url, inline=False)
        embed.set_thumbnail(url=guild.icon_url)
    embed.add_field(name='Dueño', value=f'<@!{guild.owner_id}>', inline=False)
    embed.add_field(name='Número de miembros', value=guild.member_count, inline=False)
    embed.add_field(name='(UTC) Creado el día', value=guild.created_at, inline=False)
    await ctx.send(embed=embed)


@command(help='Muestra la foto de un usuario en un tamaño grande', aliases=['image', 'photo', 'foto', 'imagen'], usage='avatar [<usuario>]')
async def avatar(ctx, member: Optional[Member]):
    member = member or ctx.author
    embed = Embed(
        title=f'Avatar de {member.display_name}'
    )
    embed.set_image(url=member.avatar_url)
    await ctx.send(embed=embed)


@command(help='Prohible un usuario en el servidor', usage='ban <usuario> [<razón>]')
@has_permissions(ban_members=True)
async def ban(ctx, member: Member, reason: Optional[str]):
    await member.ban(reason=reason)
    embed = Embed(
        title=f'Usuario baneado ✅',
        description=f'El usuario {member.name} ha sido baneado satisfactoriamente',
        color=Color.red()
    )
    await ctx.send(embed=embed)


@command(help='Permite un usuario en el servidor que anteriormente habia sido baneado', usage='unban <usuario> [<razón>]')
@has_permissions(ban_members=True)
async def unban(ctx, member: Member, reason: Optional[str]):
    await member.unban(reason=reason)
    embed = Embed(
        title=f'Usuario desbaneado ✅',
        description=f'El usuario {member.name} ha sido desbaneado satisfactoriamente',
        color=Color.red()
    )
    await ctx.send(embed=embed)


@command(help='Expulsa a un usuario del servidor', usage='kick <usuario> [<razón>]', aliases=['expulsar'])
@has_permissions(kick_members=True)
async def kick(ctx, member: Member, reason: Optional[str]):
    await member.kick(reason=reason)
    embed = Embed(
        title=f'Usuario kickeado ✅',
        description=f'El usuario {member.name} ha sido expulsado satisfactoriamente',
        color=Color.red()
    )
    await ctx.send(embed=embed)


@command(help='Evita que un usuario envie mensajes o entre a canales de voz', usage='mute <usuario> [<razón>]')
@has_permissions(manage_messages=True)
async def mute(ctx, member: Member, *args):
    role = utils.get(ctx.guild.roles, name='Muted')
    if role is None:
        role = await ctx.guild.create_role(name='Muted', color=Color.dark_grey())
        for channel in ctx.guild.channels:
            await channel.set_permissions(role, send_messages=False, speak=False)
    await member.add_roles(role)
    embed = Embed(
        title=f'Usuario silenciado ✅',
        description=f'El usuario {member.name} ha sido silenciado satisfactoriamente',
        color=Color.red()
    )
    if args:
        reason = ' '.join(args)
        embed.description += f'\nRazón: {reason}'
    await ctx.send(embed=embed)


@command(help='Permite a un usuario silenciado hablar y escribir nuevamente', usage='unmute <usuario> [<razón>]')
@has_permissions(manage_messages=True)
async def unmute(ctx, member: Member, *args):
    role = utils.get(ctx.guild.roles, name='Muted')
    await member.remove_roles(role)
    embed = Embed(
        title=f'Usuario des-silenciado ✅',
        description=f'El usuario {member.name} ha sido des-silenciado satisfactoriamente',
        color=Color.red()
    )
    if args:
        reason = ' '.join(args)
        embed.description += f'\nRazón: {reason}'
    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(hello)
    bot.add_command(clear)
    bot.add_command(info)
    bot.add_command(avatar)
    bot.add_command(ban)
    bot.add_command(unban)
    bot.add_command(kick)
    bot.add_command(mute)
    bot.add_command(unmute)
