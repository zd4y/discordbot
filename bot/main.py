from discord.ext import commands
from config import Config, ServerConfig

import logging

logging.basicConfig(filename='latest.log', level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d:%(levelname)s:%(name)s:%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


async def get_prefix(bot, msg):
    prefix = await ServerConfig.get_setting(msg.guild.id, 'prefix')
    return prefix.split()


bot = commands.Bot(command_prefix=get_prefix)

bot.load_extension('commands')

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
