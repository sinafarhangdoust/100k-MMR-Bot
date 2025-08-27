from typing import Union
from pydantic import Field

import chainlit as cl

from tools.dota_db import DotaDB
from constants import (
    HEROES,
    MECHANICS,
    ITEM_TYPE,
    NEUTRAL_ITEMS,
    SHOP_ITEMS,
    ENCHANTMENT_ITEMS,
)

def get_hero(hero_name: HEROES = Field(description="The name of the hero")):
    """ Returns full details about a specific hero """

    dota_db : DotaDB = cl.user_session.get('dota_db')
    return dota_db.get_hero(hero_name)

def get_mechanics(mechanic_name: MECHANICS = Field(description="The name of the mechanic")):
    """ Returns full details about a specific mechanic """

    dota_db : DotaDB = cl.user_session.get('dota_db')
    return dota_db.get_mechanic(mechanic_name)

def get_item(
    item_type: ITEM_TYPE = Field(description="The item type"),
    item_name: Union[NEUTRAL_ITEMS, SHOP_ITEMS, ENCHANTMENT_ITEMS] = Field(description="The name of the item"),
):
    """ Returns full details about a needed item """
    dota_db : DotaDB = cl.user_session.get('dota_db')
    return dota_db.get_item(item_type=item_type, item_name=item_name)
