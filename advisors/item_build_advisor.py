import json
import os

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


if __name__ == '__main__':
    client = OpenDotaEnhanced(data_dir='./')
    item_popularity = client.get_item_popularity(hero_id=102)
    items_list  = client.get_items()
