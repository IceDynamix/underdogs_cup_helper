import json
import requests

TETRIO_CACHE = "tetrio_cache"


def download_data(endpoint, useCache):
    cache_path = f"./{TETRIO_CACHE}/{endpoint}_cache.json"
    if useCache:
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        data = json.loads(requests.get(
            f"https://tetrio.team2xh.net/data/{endpoint}.js").text)
        with open(cache_path, "w") as f:
            json.dump(data, f)
        return data
