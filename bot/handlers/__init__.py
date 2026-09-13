from aiogram import Router

from bot.handlers import callbacks, commands, convert

router = Router(name="root")
router.include_router(commands.router)
router.include_router(callbacks.router)
router.include_router(convert.router)
