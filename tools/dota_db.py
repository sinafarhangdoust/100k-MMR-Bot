import json
from threading import Lock
from pathlib import Path
from typing import Union, Dict

from utils import S3Wrapper
from config import S3_BUCKET_NAME
from constants import ITEM_TYPE, SHOP_ITEMS, NEUTRAL_ITEMS, ENCHANTMENT_ITEMS, MECHANICS, HEROES

# TODO: change the logic to lazy loading
class DotaDB:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Prevent reinitialization on subsequent calls
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.s3_wrapper = S3Wrapper(endpoint="http://localhost:9000")

        self.heroes = {}
        self.items = {}
        self.mechanics = {}
        self._initialized = True

    def load_rag_storage(self):
        """
        Loads the entire rag storage at once
        :return: None
        """

        for obj in self.s3_wrapper.s3_client.list_objects(Bucket=S3_BUCKET_NAME).get('Contents', []):
            obj_path = Path(obj["Key"])
            loaded_obj = self.s3_wrapper.s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])["Body"].read()

            if obj_path.suffix == ".json":
                content = json.loads(loaded_obj.decode("utf-8"))
            else:
                content = loaded_obj.decode("utf-8", errors="ignore")

            if str(obj_path).startswith('heroes'):
                self.heroes[obj_path.stem] = content
            elif str(obj_path).startswith('items'):
                parent_dir = obj_path.parent.stem
                if parent_dir not in self.items:
                    self.items[parent_dir] = {}
                self.items[parent_dir][obj_path.stem] = content
            elif str(obj_path).startswith('mechanics'):
                self.mechanics[obj_path.stem] = content


    def get_hero(
        self,
        hero_name: HEROES,
    ) -> Dict:
        """
        Retrieves a hero by name in a lazy loading fashion
        :param hero_name: the name of the hero to retrieve
        :return: Dict
        """
        if hero_name not in self.heroes:
            content = self.s3_wrapper.read_object(bucket_name=S3_BUCKET_NAME, key=f"heroes/{hero_name}.json")
            self.heroes[hero_name] = content

        return self.heroes[hero_name]

    def get_mechanic(
        self,
        mechanic_name: MECHANICS,
    ) -> str:
        """
        Retrieves a mechanic by name in a lazy loading fashion
        :param mechanic_name: the name of the mechanic to retrieve
        :return: str
        """
        if mechanic_name not in self.mechanics:
            content = self.s3_wrapper.read_object(bucket_name=S3_BUCKET_NAME, key=f"mechanics/{mechanic_name}.md")
            self.mechanics[mechanic_name] = content

        return self.mechanics[mechanic_name]

    def get_item(
        self,
        item_type: ITEM_TYPE,
        item_name: Union[SHOP_ITEMS, ENCHANTMENT_ITEMS, NEUTRAL_ITEMS],
    ) -> str:
        """
        Retrieves an item by name in a lazy loading fashion
        :param item_type: the type of item to retrieve
        :param item_name: the name of the item to retrieve
        :return: str
        """
        if item_type not in self.items:
            content  = self.s3_wrapper.read_object(bucket_name=S3_BUCKET_NAME, key=f"items/{item_type}/{item_name}.md")
            self.items[item_type] = {item_name: content}
            return content
        else:
            if item_name not in self.items[item_type]:
                content = self.s3_wrapper.read_object(bucket_name=S3_BUCKET_NAME, key=f"items/{item_type}/{item_name}.md")
                self.items[item_type] = {item_name: content}
                return content
            else:
                return self.items[item_type][item_name]
