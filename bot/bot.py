from discord.ext import commands
from config import Config, ServerConfig
import aiohttp


async def get_prefix(bot, msg):
    prefix = await ServerConfig.get_setting(msg.guild.id, 'prefix')
    return prefix.split()


class Bot(commands.Bot):
    """A subclass of `discord.ext.commands.Bot` with an aiohttp session."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = None

    async def start(self, *args, **kwargs):
        """Open an aiohttp session before logging in and connecting to Discord."""
        self.session = aiohttp.ClientSession()
        await super().start(*args, **kwargs)

    async def close(self, *args, **kwargs):
        """Close the aiohttp session after closing the Discord connection."""
        await super().close()
        await self.session.close()


bot = Bot(command_prefix=get_prefix)

bot.load_extension('commands')


def main():
    return bot.run(Config.DISCORD_TOKEN)


if __name__ == "__main__":
    main()
