from tools.hero_db import HeroDB


def get_hero(hero_name: str):
    hero_db = HeroDB()
    return hero_db.heroes.get(hero_name)