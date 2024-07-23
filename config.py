import json
import os

class Config:
    def __init__(self):
        self.config_file = 'browser_config.json'
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()

    def create_default_config(self):
        default_config = {
            'search_engines': {
                "Google": "https://www.google.com/search?q={}",
                "Bing": "https://www.bing.com/search?q={}",
                "DuckDuckGo": "https://duckduckgo.com/?q={}"
            },
            'default_search_engine': "Google",
            'background_color': "#FFFFFF",
            'icon_path': "",
        }
        self.save_config(default_config)
        return default_config

    def save_config(self, config=None):
        if config is None:
            config = self.config
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()