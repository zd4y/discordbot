from .bot import Bot
from .database import session
from .utils import get_prefix

from discord import Message
from discord.ext.commands import Context


bot = Bot(command_prefix=get_prefix)

bot.remove_command('help')


@bot.check
async def block_dms(ctx: Context):
    return ctx.guild is not None


@bot.event
async def on_message(msg: Message):
    session()
    await bot.process_commands(msg)
    session.remove()


bot.load_extension('bot.cogs')
bot.load_extension('bot.commands')
