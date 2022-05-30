from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from app.config import Settings


async def set_commands(bot: Bot, settings: Settings):
    commands = [
        BotCommand(
            command="start",
            description="Start",
        ),
    ]

    admin_commands = commands.copy()
    admin_commands.append(
        BotCommand(
            command="admin",
            description="Admin panel",
        )
    )

    await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())

    for admin_id in settings.tg_bot.admin_ids:
        await bot.set_my_commands(
            commands=admin_commands,
            scope=BotCommandScopeChat(
                chat_id=admin_id,
            ),
        )
