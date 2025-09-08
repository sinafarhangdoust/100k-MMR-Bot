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
from advisors.item_build_advisor import ItemAdvisor, normalize_hero_name


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

def get_hero_item_suggestion(hero_name: HEROES = Field(description="The name of the hero")):
    """ Returns suggested items that a hero should buy for each stage """
    item_advisor = ItemAdvisor()
    hero_name = normalize_hero_name(hero_name.lower())

    return item_advisor.get_item_suggestion(hero_name)
