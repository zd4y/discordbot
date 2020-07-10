from .user import UserCmds
from .bot_config import BotConfigCmds
from .moderation import ModerationCmds
from .unmoderation import UnModerationCmds
from .verification import Verification
from .server_config import ServerConfigCmds


def setup(bot):
    bot.add_cog(Verification(bot))
    bot.add_cog(UserCmds(bot))
    bot.add_cog(ModerationCmds(bot))
    bot.add_cog(UnModerationCmds(bot))
    bot.add_cog(ServerConfigCmds(bot))
    bot.add_cog(BotConfigCmds(bot))
