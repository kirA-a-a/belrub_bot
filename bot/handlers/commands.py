from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.keyboards import after_convert_keyboard, direction_keyboard
from bot.services.convert import format_rate_line
from bot.services.rates import RateService
from bot.storage.directions import DirectionStore

router = Router(name="commands")


def _ask_direction_text() -> str:
    return "Из какой валюты конвертируем?"


@router.message(CommandStart())
async def cmd_start(message: Message, directions: DirectionStore) -> None:
    assert message.from_user
    direction = directions.get(message.from_user.id)
    if direction is None:
        await message.answer(
            "Привет! Я бот конвертации RUB ↔ BYN.\n\n" + _ask_direction_text(),
            reply_markup=direction_keyboard(),
        )
        return

    await message.answer(
        "Снова привет!\n"
        f"Сейчас направление: {direction.label}.\n"
        "Пришли сумму числом, например 1000 или 50.5.\n"
        "Сменить направление: /direction",
        reply_markup=after_convert_keyboard(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(
        "Как пользоваться:\n"
        "1. Выбери направление: /direction\n"
        "2. Пришли сумму числом: 1000 или 50.5\n"
        "3. Можно разово указать валюту: 1000 RUB или 50 BYN "
        "(дефолт не меняется)\n\n"
        "Команды:\n"
        "/start — старт\n"
        "/help — эта справка\n"
        "/rate — текущий курс\n"
        "/direction или /change — сменить направление\n"
        "/my — текущее направление"
    )


@router.message(Command("rate"))
async def cmd_rate(message: Message, rates: RateService) -> None:
    try:
        quote = await rates.get_quote()
    except RuntimeError as exc:
        await message.answer(f"Не удалось получить курс: {exc}")
        return
    await message.answer(format_rate_line(quote))


@router.message(Command("direction"))
@router.message(Command("change"))
async def cmd_direction(message: Message) -> None:
    await message.answer(_ask_direction_text(), reply_markup=direction_keyboard())


@router.message(Command("my"))
async def cmd_my(message: Message, directions: DirectionStore) -> None:
    assert message.from_user
    direction = directions.get(message.from_user.id)
    if direction is None:
        await message.answer(
            "Направление ещё не выбрано.\n" + _ask_direction_text(),
            reply_markup=direction_keyboard(),
        )
        return
    await message.answer(
        f"Сейчас: {direction.label}.\nПришли сумму или смени через /direction",
        reply_markup=after_convert_keyboard(),
    )
