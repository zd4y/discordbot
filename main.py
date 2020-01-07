from discord.ext import commands
from discord import Color, Embed, utils, Game
from config import TOKEN, get_prefix, set_prefix
from util import Checks


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')

bot.load_extension('commands')


@bot.command(help='Recarga algunos comandos del bot', usage='reload [<extención>]')
@commands.check(Checks.is_admin)
async def reload(ctx, *args):
    if args:
        for arg in args:
            bot.reload_extension(arg)
    else:
        bot.reload_extension('commands')
    embed = Embed(
        title='Reloaded ✅',
        color=Color.red(),
        description='Bot recargado satisfactoriamente!'
    )
    await ctx.send(embed=embed)


@bot.command(help='Muestra ayuda acerca del bot', aliases=['ayuda', 'comandos', 'commands'], usage='help [<comando>]')
async def help(ctx, command=None):
    if command:
        cmd = utils.get(bot.commands, name=command)
        if cmd.aliases:
            aliases = ', '.join(cmd.aliases)
        embed = Embed(
            title=f'Ayuda sobre el comando {cmd.name}',
            description=f'{cmd.help}\nAlias: {aliases}\nUso: `{cmd.usage}`'
        )
        await ctx.send(embed=embed)
    else:
        embed = Embed(
            title='Ayuda',
            description=f'Prefix: {ctx.prefix}\n\nLista de comandos del bot:',
            color=Color.red()
        )
        for cmd in bot.commands:
            value = cmd.help
            if cmd.aliases:
                aliases = ', '.join(cmd.aliases)
                value += f'\nAlias: {aliases}'
                value += f'\nUso: `{ctx.prefix}{cmd.usage}`'

            embed.add_field(name=cmd.name, value=value, inline=False)

        await ctx.send(embed=embed)


@bot.command(help='Muestra el prefix del bot o lo cambia, puedes usar múltiples prefixes pasando varios separados por espacios', usage='prefix [<nuevos prefixes>]')
@commands.check(Checks.can_manage_server)
async def prefix(ctx, *args):
    if args:
        set_prefix(ctx.message, *args)
        prefixes = bot.command_prefix(bot, ctx.message)
        if isinstance(prefixes, list):
            prefixes = ', '.join(prefixes)
        embed = Embed(
            title='Prefix editado! ✅',
            description=f'Los prefixes ahora son: {prefixes}',
            color=Color.red()
        )
        await ctx.send(embed=embed)
    else:
        prefixes = bot.command_prefix(bot, ctx.message)
        if isinstance(prefixes, list):
            prefixes = ', '.join(prefixes)
        embed = Embed(
            title='Prefix del Bot',
            description=f'Los prefixes actuales son: {prefixes}',
            color=Color.red()
        )
        await ctx.send(embed=embed)


@bot.event
async def on_command_error(ctx, error):
    cmd = ctx.message.content.split()[0]
    embed = Embed(
        title='Error ❌',
        color=Color.red()
    )
    if isinstance(error, commands.CommandNotFound):
        embed.description = f'El comando `{cmd}` no existe.\nPuedes utilizar `{ctx.prefix}help` para ver una lista detallada de los comandos disponibles.'
    elif isinstance(error, commands.CheckFailure):
        embed.description = f'No tienes permisos suficientes para usar ese comando.'
    else:
        embed.description = 'Error desconocido'
        print(error)
    await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    default_role = utils.get(member.guild.roles, position=1)
    await member.add_roles(default_role)

    if channel:
        embed = Embed(
            title=f'Bienvenido {member.display_name} a {member.guild.name}',
            description='Por favor lee las reglas.',
            color=Color.red()
        )
        embed.set_thumbnail(url=member.avatar_url_as(size=256))
        await channel.send(embed=embed)


@bot.event
async def on_ready():
    activity = Game('default prefix: !')
    await bot.change_presence(activity=activity)
    print('Bot is ready.')


bot.run(TOKEN)
