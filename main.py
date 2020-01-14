from discord.ext import commands
from config import Config, ServerConfig


async def get_prefix(bot, msg):
    prefix = await ServerConfig.get_setting(msg.guild.id, 'prefix')
    return prefix.split()


bot = commands.Bot(command_prefix=get_prefix)

bot.load_extension('commands')

bot.run(Config.DISCORD_TOKEN)
