from aiogram import F, Router
from aiogram.types import Message

from bot.keyboards import after_convert_keyboard, direction_keyboard
from bot.services.convert import format_convert_reply, parse_amount_message
from bot.services.rates import RateService
from bot.storage import Direction
from bot.storage.directions import DirectionStore

router = Router(name="convert")


@router.message(F.text)
async def convert_message(
    message: Message,
    directions: DirectionStore,
    rates: RateService,
) -> None:
    assert message.from_user
    text = (message.text or "").strip()
    if text.startswith("/"):
        return

    parsed = parse_amount_message(text)
    if parsed is None:
        await message.answer(
            "Не понял сумму.\n"
            "Пришли число, например: 1000 или 50.5\n"
            "Или с валютой: 1000 RUB / 50 BYN"
        )
        return

    saved = directions.get(message.from_user.id)

    if parsed.currency is None:
        if saved is None:
            await message.answer(
                "Сначала выбери направление конвертации.",
                reply_markup=direction_keyboard(),
            )
            return
        direction = saved
    else:
        # Explicit currency for this message only — default unchanged
        if parsed.currency == "RUB":
            direction = Direction.RUB_TO_BYN
        else:
            direction = Direction.BYN_TO_RUB
        if saved is None:
            await message.answer(
                "Направление по умолчанию ещё не выбрано — "
                "это разовая конвертация.\n"
                "Чтобы задать дефолт: /direction",
                reply_markup=direction_keyboard(),
            )

    try:
        quote = await rates.get_quote()
    except RuntimeError as exc:
        await message.answer(f"Курс недоступен: {exc}")
        return

    reply = format_convert_reply(parsed.amount, direction, quote)
    await message.answer(reply, reply_markup=after_convert_keyboard())
