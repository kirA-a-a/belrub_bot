from enum import StrEnum


class Direction(StrEnum):
    RUB_TO_BYN = "RUB_TO_BYN"
    BYN_TO_RUB = "BYN_TO_RUB"

    @property
    def label(self) -> str:
        if self is Direction.RUB_TO_BYN:
            return "RUB → BYN"
        return "BYN → RUB"

    @property
    def from_currency(self) -> str:
        return "RUB" if self is Direction.RUB_TO_BYN else "BYN"

    @property
    def to_currency(self) -> str:
        return "BYN" if self is Direction.RUB_TO_BYN else "RUB"
