from .bot import Bot
from .utils import get_prefix
from .database import session


bot = Bot(command_prefix=get_prefix)


@bot.check
async def block_dms(ctx):
    return ctx.guild is not None


@bot.event
async def on_message(msg):
    session()
    await bot.process_commands(msg)
    session.remove()


bot.load_extension('bot.commands')
