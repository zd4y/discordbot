from discord.ext import commands
from config import Config


# TODO Get command prefix from guild config
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')

bot.load_extension('commands')

bot.run(Config.DISCORD_TOKEN)
