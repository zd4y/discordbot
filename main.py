from discord.ext import commands
from config import Config, ServerConfig


def get_prefix(bot, msg):
    return ServerConfig.get_setting(msg.guild.id, 'prefix').split()


bot = commands.Bot(command_prefix=get_prefix)

bot.load_extension('commands')

bot.run(Config.DISCORD_TOKEN)
