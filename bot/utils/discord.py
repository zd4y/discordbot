from .. import crud
from ..models import VerificationRole, Guild

import discord
from typing import List, Optional
from discord import Message, HTTPException
from discord.ext.commands import Bot, Context, when_mentioned_or


def get_prefix(bot: Bot, msg: Message):
    guild = crud.get_guid(msg.guild.id)
    prefix_setting = crud.get_guild_setting(guild, 'prefix')
    prefixes = prefix_setting.split()
    return when_mentioned_or(*prefixes)(bot, msg)


def display_role(ctx: Context, db_role: VerificationRole, include_id=False):
    role = discord.utils.get(ctx.guild.roles, id=db_role.role_id)
    value = f'{db_role.emoji} {role.mention}\n'

    if include_id:
        value = f'`{db_role.id}`: {value}'

    return value


async def display_roles(
        ctx: Context, roles: List[VerificationRole], include_id=False, message: Optional[Message] = None
):
    value = ''

    for role in roles:
        good_emoji = True

        if message:
            try:
                await message.add_reaction(role.emoji)
            except HTTPException:
                good_emoji = False
                await ctx.send(
                    f'El rol con id {role.id} tiene un emoji al cual el bot no tiene acceso. Por favor eliminalo.'
                )

        if good_emoji:
            value += display_role(ctx, role, include_id) + '\n'

    return value


async def get_verification_message(bot: Bot, guild: Guild) -> Optional[Message]:
    message_id = crud.get_guild_setting(guild, 'verification_message')
    channel_id = crud.get_guild_setting(guild, 'verification_channel')

    message = None

    if message_id and message_id.isdigit() and channel_id and channel_id.isdigit():
        channel = bot.get_channel(int(channel_id))
        message = await channel.fetch_message(int(message_id))

    return message


async def update_message(bot: Bot, ctx: Context):
    guild = crud.get_guid(ctx.guild.id)
    text = crud.get_guild_setting(guild, 'verification_message_text')
    message = await get_verification_message(bot, guild)

    if message:
        roles = crud.get_verification_roles(ctx.guild.id)

        value = text or ''
        value += '\n\n' + await display_roles(ctx, roles, message=message)

        if not value.strip():
            return

        embed = discord.Embed(
            title='Verificación',
            description=value,
            color=discord.Color.red()
        )

        await message.edit(content=None, embed=embed)
