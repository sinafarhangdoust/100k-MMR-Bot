from pydantic import Field

import chainlit as cl

from tools.dota_db import DotaDB
from constants import HEROES, MECHANICS

def get_hero(hero_name: HEROES = Field(description="The name of the hero")):
    """ Returns full details about a specific hero """

    dota_db : DotaDB = cl.user_session.get('dota_db')
    return dota_db.heroes.get(hero_name)

def get_mechanics(mechanic_name: MECHANICS = Field(description="The name of the mechanic")):
    """ Returns full details about a specific mechanic """

    dota_db : DotaDB = cl.user_session.get('dota_db')
    return dota_db.mechanics.get(mechanic_name)