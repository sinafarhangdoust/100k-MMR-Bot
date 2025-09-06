import json
import os
from typing import Dict

from opendota import OpenDota

class OpenDotaEnhanced(OpenDota):

    def get_item_popularity(self, hero_id: int or str, force: bool = False):
        url = f"/heroes/{hero_id}/itemPopularity?"
        filename = f"item_popularity_{hero_id}.json"
        return self.get(url, filename=filename, force=force)

    def get_items(self, force: bool = False):
        sql_query = "select * from items"
        filename = f"items.json"

        path = None
        if filename is not None:
            path = os.path.join(self.data_dir, filename)
            if not force and os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                    return json_data
                except Exception:
                    pass

        json_data = self.explorer(sql_query)
        if path is not None:
            with open(path, "w", encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False)

        return json_data

class ItemAdvisor:

    def __init__(self):
        self.base_image_url = "https://cdn.cloudflare.steamstatic.com"
        self.opendota_client = OpenDotaEnhanced(data_dir='./cache')
        self.hero2id, self.id2hero = self._get_hero_to_id_mapping()
        self.item2id, self.id2item = self._get_item_to_id_mapping()


    def _get_hero_to_id_mapping(self):
        heroes = self.opendota_client.get_constants('heroes').get('heroes')
        hero2id = {hero['localized_name']: hero['id'] for id, hero in heroes.items()}
        id2hero = {hero['id']: hero for id, hero in heroes.items()}

        return hero2id, id2hero

    def _get_item_to_id_mapping(self):
        keep = {"abilities", "cost", "dname", "hint", "img", "id"}
        items = self.opendota_client.get_constants('items').get('items')
        for name, item_dict in items.items():
            items[name] = {k: v for k, v in item_dict.items() if k in keep}

        item2id = {item['dname']: item['id'] for name, item in items.items() if 'dname' in item}
        id2item = {item['id']: item for name, item in items.items() if 'dname' in item}

        return item2id, id2item

    def get_hero_name(self, hero_id: int or str):
        if isinstance(hero_id, str):
            hero_id = int(hero_id)
        return self.id2hero[hero_id]

    def get_hero_id(self, hero_name: str):
        return self.hero2id[hero_name]

    def get_item_name(self, item_id: int or str):
        if isinstance(item_id, str):
            item_id = int(item_id)
        return self.id2item[item_id]

    def get_item_id(self, item_name: str):
        return self.item2id[item_name]

    def get_item_suggestion(self, hero_name: str) -> Dict:
        hero_id = self.get_hero_id(hero_name)
        raw_item_popularity = self.opendota_client.get_item_popularity(hero_id=hero_id)
        item_popularity = {}
        for stage, item_dict in raw_item_popularity.items():
            item_popularity[stage] = []
            for item_id, frequency in item_dict.items():
                item_name = self.get_item_name(item_id)
                item_popularity[stage].append((frequency, item_name))
            item_popularity[stage].sort(key=lambda x: x[0], reverse=True)
            item_popularity[stage] = [(item[1]['dname'], item[1]) for item in item_popularity[stage]]


        return item_popularity