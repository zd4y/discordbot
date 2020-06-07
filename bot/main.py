from .bot import Bot
from .database import session
from .utils import get_prefix


bot = Bot(command_prefix=get_prefix)


@bot.check
async def block_dms(ctx):
    return ctx.guild is not None


async def before_invoke(ctx):
    session()


async def after_invoke(ctx):
    session.remove()


bot.before_invoke(before_invoke)
bot.after_invoke(after_invoke)

bot.load_extension('bot.commands')
