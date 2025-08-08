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
        self.summary_info = None
        self.basic_stats = None
        self.facets = None
        self.innate = None
        self.scepter_upgrade_info = None
        self.shard_upgrade_info = None
        self.talent_tree = None
        self.main_attribute = ''
        self.abilities = []

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'name': self.name,
            'title': self.title,
            'quote': self.quote,
            'lore_summary': self.lore_summary,
            'summary_info': self.summary_info,
            'basic_stats': self.basic_stats,
            'facets': self.facets,
            'innate': self.innate,
            'scepter_upgrade_info': self.scepter_upgrade_info,
            'shard_upgrade_info': self.shard_upgrade_info,
            'talent_tree': self.talent_tree,
            'main_attribute': self.main_attribute,
            'abilities': self.abilities
        }