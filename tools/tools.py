from pydantic import Field

from tools.hero_db import HeroDB
from constants import HEROES

def get_hero(hero_name: HEROES = Field(description="The name of the hero")):
    hero_db = HeroDB()
    return hero_db.heroes.get(hero_name)