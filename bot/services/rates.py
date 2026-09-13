from __future__ import annotations

import logging
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RateQuote:
    """How many BYN for 1 RUB."""

    rub_to_byn: float
    source: str
    fetched_at: float

    @property
    def byn_to_rub(self) -> float:
        return 1.0 / self.rub_to_byn


class RateService:
    def __init__(self, cache_ttl_seconds: int = 3600) -> None:
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: RateQuote | None = None

    async def get_quote(self) -> RateQuote:
        if self._cache and (time.time() - self._cache.fetched_at) < self.cache_ttl_seconds:
            return self._cache

        errors: list[str] = []
        for fetcher in (self._fetch_nbrb, self._fetch_cbr):
            try:
                quote = await fetcher()
                self._cache = quote
                return quote
            except Exception as exc:  # noqa: BLE001 — try next source
                errors.append(f"{fetcher.__name__}: {exc}")
                logger.warning("Rate fetch failed via %s: %s", fetcher.__name__, exc)

        raise RuntimeError("Не удалось получить курс. Источники: " + "; ".join(errors))

    async def _fetch_nbrb(self) -> RateQuote:
        # Cur_Scale RUB units cost Cur_OfficialRate BYN
        url = "https://api.nbrb.by/exrates/rates/RUB?parammode=2"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        scale = float(data["Cur_Scale"])
        official = float(data["Cur_OfficialRate"])
        rub_to_byn = official / scale
        return RateQuote(
            rub_to_byn=rub_to_byn,
            source="НБРБ",
            fetched_at=time.time(),
        )

    async def _fetch_cbr(self) -> RateQuote:
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            root = ET.fromstring(response.content)

        for valute in root.findall("Valute"):
            char_code = valute.findtext("CharCode")
            if char_code != "BYN":
                continue
            nominal = float(valute.findtext("Nominal") or "1")
            value_raw = (valute.findtext("Value") or "").replace(",", ".")
            value = float(value_raw)
            # value RUB for `nominal` BYN → 1 RUB = nominal/value BYN
            rub_to_byn = nominal / value
            return RateQuote(
                rub_to_byn=rub_to_byn,
                source="ЦБ РФ",
                fetched_at=time.time(),
            )

        raise ValueError("BYN не найден в ответе ЦБ РФ")
