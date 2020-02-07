from .bot import Bot
from .config import Config, ServerConfig


async def get_prefix(bot, msg):
    prefix = await ServerConfig.get_setting(msg.guild.id, 'prefix')
    return prefix.split()


bot = Bot(command_prefix=get_prefix)

bot.load_extension('bot.commands')

bot.run(Config.DISCORD_TOKEN)
