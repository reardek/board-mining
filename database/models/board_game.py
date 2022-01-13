from typing import TypedDict
from .base import Base
from odmantic import Model

class BoardGameDetails(Model):
    title: str
    description: str
    image: str
    bgg_link: str

class BoardGameLinks(TypedDict):
    rebel: str
    three_trolls: str
    bez_pradu: str
                