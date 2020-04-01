from .bot import Bot
from .config import Config, ServerConfig
from discord.ext.commands import when_mentioned_or


async def get_prefix(bot, msg):
    prefix = await ServerConfig.get_setting(msg.guild.id, 'prefix')
    prefixes = prefix.split()
    return when_mentioned_or(*prefixes)(bot, msg)


bot = Bot(command_prefix=get_prefix)


@bot.check
async def block_dms(ctx):
    return ctx.guild is not None

bot.load_extension('bot.commands')

bot.run(Config.DISCORD_TOKEN)
