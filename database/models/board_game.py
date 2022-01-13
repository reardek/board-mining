from typing import TypedDict
from .base import Base

class BoardGameDetails(Base):
    title: str
    description: str
    image: str
    bgg_link: str

class BoardGameLinks(TypedDict):
    rebel: str
    three_trolls: str
    bez_pradu: str
                