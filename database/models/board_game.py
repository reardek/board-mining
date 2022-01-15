from datetime import datetime
from typing import Optional, TypedDict, List

from odmantic import EmbeddedModel, Model
from .base import Base


class BoardGamePriceHistory(EmbeddedModel):
    date: datetime
    shop: str
    price: float


class BoardGameLinks(EmbeddedModel):
    rebel: str
    three_trolls: str
    bez_pradu: str


class BggDetails(EmbeddedModel):
    title: str
    description: str
    image: str
    bgg_link: str


class BoardGameDetails(Model):
    bgg_details: BggDetails
    shop_links: BoardGameLinks
    available: Optional[bool]
    current_price: Optional[float]
    price_history: List[BoardGamePriceHistory] = []
