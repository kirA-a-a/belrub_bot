from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone

from bot.services.rates import RateQuote
from bot.storage import Direction

AMOUNT_RE = re.compile(
    r"^\s*(?P<amount>\d+(?:[.,]\d+)?)\s*"
    r"(?P<currency>RUB|BYN|BYR|РУБ|РУБЛ|Р|БРН|БЕЛ)?\s*$",
    re.IGNORECASE,
)

CURRENCY_ALIASES = {
    "RUB": "RUB",
    "Р": "RUB",
    "РУБ": "RUB",
    "РУБЛ": "RUB",
    "BYN": "BYN",
    "БРН": "BYN",
    "БЕЛ": "BYN",
    "BYR": "BYN",
}


@dataclass(frozen=True)
class ParsedAmount:
    amount: float
    currency: str | None  # RUB/BYN or None = use default direction


def parse_amount_message(text: str) -> ParsedAmount | None:
    match = AMOUNT_RE.match(text.strip())
    if not match:
        return None
    amount = float(match.group("amount").replace(",", "."))
    if amount <= 0 or amount > 1e12:
        return None
    raw_currency = match.group("currency")
    currency = None
    if raw_currency:
        currency = CURRENCY_ALIASES.get(raw_currency.upper())
    return ParsedAmount(amount=amount, currency=currency)


def convert_amount(amount: float, direction: Direction, quote: RateQuote) -> float:
    if direction is Direction.RUB_TO_BYN:
        return amount * quote.rub_to_byn
    return amount * quote.byn_to_rub


def format_money(value: float, currency: str) -> str:
    if value >= 100:
        text = f"{value:,.2f}"
    elif value >= 1:
        text = f"{value:,.4f}"
    else:
        text = f"{value:,.6f}"
    return f"{text.replace(',', ' ')} {currency}"


def format_rate_line(quote: RateQuote) -> str:
    updated = datetime.fromtimestamp(quote.fetched_at, tz=timezone.utc).astimezone()
    updated_str = updated.strftime("%d.%m.%Y %H:%M")
    return (
        f"Курс: 1 RUB = {quote.rub_to_byn:.6f} BYN\n"
        f"Источник: {quote.source} | обновлён: {updated_str}"
    )


def format_convert_reply(
    amount: float,
    direction: Direction,
    quote: RateQuote,
) -> str:
    result = convert_amount(amount, direction, quote)
    return (
        f"{format_money(amount, direction.from_currency)} = "
        f"{format_money(result, direction.to_currency)}\n"
        f"{format_rate_line(quote)}"
    )
