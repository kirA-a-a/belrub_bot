from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards import direction_keyboard
from bot.storage import Direction
from bot.storage.directions import DirectionStore

router = Router(name="callbacks")


@router.callback_query(F.data == "dir:ask")
async def ask_direction(callback: CallbackQuery) -> None:
    await callback.answer()
    if callback.message:
        await callback.message.answer(
            "Из какой валюты конвертируем?",
            reply_markup=direction_keyboard(),
        )


@router.callback_query(F.data.in_({f"dir:{Direction.RUB_TO_BYN}", f"dir:{Direction.BYN_TO_RUB}"}))
async def set_direction(callback: CallbackQuery, directions: DirectionStore) -> None:
    assert callback.from_user
    assert callback.data
    direction = Direction(callback.data.removeprefix("dir:"))
    directions.set(callback.from_user.id, direction)
    await callback.answer("Сохранено")
    if callback.message:
        await callback.message.answer(
            f"Ок. Сейчас: {direction.label}. Пришли сумму."
        )
