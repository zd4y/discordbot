from discord.ext import commands
from discord import Color, Embed, utils, Game, Forbidden
from config import TOKEN, get_prefix, set_prefix


bot = commands.Bot(command_prefix=get_prefix)
bot.remove_command('help')

bot.load_extension('commands')


@bot.command(help='Recarga algunos comandos del bot', usage='reload [<extención>]')
@commands.has_permissions(administrator=True)
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
        embed = Embed(
            title=f'Ayuda sobre el comando {cmd.name}',
            description=f'{cmd.help}\nUso: `{ctx.prefix}{cmd.usage}`',
            color=Color.red()
        )
        if cmd.aliases:
            aliases = ', '.join(cmd.aliases)
            embed.description += f'\nAlias: {aliases}'
        await ctx.send(embed=embed)
    else:
        embed = Embed(
            title='Ayuda',
            description=f'Prefix: {ctx.prefix}\n\nLista de comandos del bot:',
            color=Color.red()
        )
        for cmd in bot.commands:
            value = cmd.help
            value += f'\nUso: `{ctx.prefix}{cmd.usage}`'
            if cmd.aliases:
                aliases = ', '.join(cmd.aliases)
                value += f'\nAlias: {aliases}'

            embed.add_field(name=cmd.name, value=value, inline=False)

        await ctx.send(embed=embed)


@bot.command(help='Muestra el prefix del bot o lo cambia, puedes usar múltiples prefixes pasando varios separados por espacios', usage='prefix [<nuevos prefixes>]')
@commands.has_permissions(manage_guild=True)
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
        embed.description = 'No tienes permisos suficientes para usar ese comando.'
    elif isinstance(error, Forbidden):
        embed.description = 'El bot no tiene permisos suficientes para realizar esa acción'
    elif isinstance(error, commands.MissingRequiredArgument):
        embed.description = f'Faltan argumentos. Revisa el `{ctx.prefix}help {ctx.command}` para obtener ayuda acerca del comando.'
    else:
        embed.description = 'Error desconocido'
        print(error, error.__class__)
    await ctx.send(embed=embed)


@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    default_role = utils.get(member.guild.roles, name='Miembro')
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
