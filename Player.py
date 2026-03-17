"""Player data model for OSM transfer-list analysis."""

from dataclasses import dataclass, field
from functools import total_ordering


@total_ordering
@dataclass
class Player:
    name: str
    pos: str
    age: str
    club: str
    att: int
    deff: int
    ovr: int
    priceToBuy: int
    realPrice: int
    inflated: float = field(init=False)
    avrMedia: int = field(init=False)

    def __post_init__(self) -> None:
        self.inflated = (self.priceToBuy - self.realPrice) / self.realPrice * 100
        self.avrMedia = (self.att + self.deff + self.ovr) // 3

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Player):
            return NotImplemented
        return (self.inflated, self.avrMedia) == (other.inflated, other.avrMedia)

    def __lt__(self, other: "Player") -> bool:
        # Primary: lowest inflation first; secondary: highest avrMedia first
        return (self.inflated, -self.avrMedia) < (other.inflated, -other.avrMedia)

    def __str__(self) -> str:
        return (
            f"Nombre: {self.name}, Posición: {self.pos}, Edad: {self.age}, Club: {self.club}, "
            f"Ataque: {self.att}, Defensa: {self.deff}, OVR: {self.ovr}, "
            f"Compra: {self.priceToBuy:,}, Real: {self.realPrice:,}, Inflación: {self.inflated:.2f}%"
        )