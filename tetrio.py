import json
import requests
import os

TETRIO_CACHE = "tetrio_cache"


def retrieve_data(endpoint: str, use_cache: bool = True):
    if not os.path.exists(TETRIO_CACHE):
        os.mkdir(TETRIO_CACHE)

    cache_path = f"./{TETRIO_CACHE}/{endpoint}.json"
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)
    else:
        data = json.loads(requests.get(
            f"https://tetrio.team2xh.net/data/{endpoint}.js").text)
        with open(cache_path, "w+") as f:
            json.dump(data, f)
        return data


if __name__ == "__main__":
    retrieve_data("players")
