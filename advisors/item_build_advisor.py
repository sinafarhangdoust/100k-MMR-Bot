from opendota import OpenDota

class OpenDotaEnhanced(OpenDota):

    def get_item_popularity(self, hero_id: int or str, force: bool = False):
        url = f"/heroes/{hero_id}/itemPopularity?"
        filename = f"item_popularity_{hero_id}.json"
        return self.get(url, filename=filename, force=force)


if __name__ == '__main__':
    client = OpenDotaEnhanced(data_dir='./')
    item_popularity = client.get_item_popularity(hero_id=102)
    heroes = client.get_heroes()
    print()
