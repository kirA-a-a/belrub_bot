from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.storage import Direction


def direction_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Из RUB (в BYN)",
                    callback_data=f"dir:{Direction.RUB_TO_BYN.value}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Из BYN (в RUB)",
                    callback_data=f"dir:{Direction.BYN_TO_RUB.value}",
                )
            ],
        ]
    )


def after_convert_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Сменить направление",
                    callback_data="dir:ask",
                )
            ]
        ]
    )
