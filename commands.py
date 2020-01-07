from discord.ext.commands import command, check
from discord import Embed, Member, Color
from util import Checks
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
@check(Checks.can_manage_messages)
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
async def ban(ctx, member: Optional[Member], reason=None):
    await member.ban(reason=reason)
    embed = Embed(
        title=f'Usuario baneado ✅',
        description=f'El usuario {member.name} ha sido baneado satisfactoriamente'
    )
    await ctx.send(embed=embed)


@command(help='Permite un usuario en el servidor que anteriormente habia sido baneado', usage='unban <usuario> [<razón>]')
async def unban(ctx, member: Optional[Member], reason=None):
    await member.unban(reason=reason)
    embed = Embed(
        title=f'Usuario desbaneado ✅',
        description=f'El usuario {member.name} ha sido desbaneado satisfactoriamente'
    )
    await ctx.send(embed=embed)


def setup(bot):
    bot.add_command(hello)
    bot.add_command(clear)
    bot.add_command(info)
    bot.add_command(avatar)
    bot.add_command(ban)
    bot.add_command(unban)
