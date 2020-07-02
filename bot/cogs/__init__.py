from .loops import Loops
from .listeners import Listeners


def setup(bot):
    bot.add_cog(Listeners(bot))
    bot.add_cog(Loops(bot))
