import json
from threading import Lock
from pathlib import Path

from utils import instantiate_s3_client
from config import S3_BUCKET_NAME

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

    def load_rag_storage(self):

        for obj in self.s3_client.list_objects(Bucket=S3_BUCKET_NAME).get('Contents', []):
            obj_path = Path(obj["Key"])
            loaded_obj = self.s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=obj["Key"])["Body"].read()

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

    def __init__(self):
        # Prevent reinitialization on subsequent calls
        if hasattr(self, "_initialized") and self._initialized:
            return

        self.s3_client = instantiate_s3_client()

        self.heroes = {}
        self.items = {}
        self.mechanics = {}
        self.load_rag_storage()
        self._initialized = True
