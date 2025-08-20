import glob
import json
from threading import Lock

class HeroDB:
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

        self.heroes = {}
        for file in glob.glob("heroes/*"):
            with open(file) as json_file:
                hero_data = json.load(json_file)
            self.heroes[hero_data['name']] = hero_data

        self._initialized = True
