from .bot import Bot
from .database import session
from .utils import get_prefix, use_db


bot = Bot(command_prefix=get_prefix)


@bot.check
async def block_dms(ctx):
    return ctx.guild is not None


@bot.event
@use_db
async def on_message(msg):
    await bot.process_commands(msg)


bot.load_extension('bot.commands')
