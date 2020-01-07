# Checks
class Checks:
    @staticmethod
    def is_admin(ctx):
        return ctx.author.permissions_in(ctx.channel).administrator

    @staticmethod
    def can_manage_server(ctx):
        return ctx.author.permissions_in(ctx.channel).manage_guild

    @staticmethod
    def can_manage_channel(ctx):
        return ctx.author.permissions_in(ctx.channel).manage_channels

    @staticmethod
    def can_manage_messages(ctx):
        return ctx.author.permissions_in(ctx.channel).manage_messages
