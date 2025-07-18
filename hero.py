from abc import ABC

class Ability:
    def __init__(self):
        self.name = None


class Hero:

    def __init__(self, name: str):
        self.name = name
        self.title = None
        self.quote = None
        self.lore_summary = None
        self.basic_stats = None
        self.facets = None
        self.innate = None
        self.scepter_upgrade_info = None
        self.shard_upgrade_info = None
        self.talent_tree = None
        self.main_attribute = ''

