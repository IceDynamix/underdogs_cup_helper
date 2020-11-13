import json
import os
import discord

import requests

TETRIO_CACHE = "tetrio_cache"
RANK_COLORS = {
    "d": "856C84",
    "dp": "815880",
    "cm": "6C417C",
    "c": "67287B",
    "cp": "522278",
    "bm": "5949BE",
    "b": "4357B5",
    "bp": "4880B2",
    "am": "35AA8C",
    "a": "3EA750",
    "ap": "43b536",
    "sm": "B79E2B",
    "s": "d19e26",
    "sp": "dbaf37",
    "ss": "e39d3b",
    "u": "c75c2e",
    "x": "b852bf",
    "z": "828282"
}


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


def generate_embed(username: str = None):
    playerbase_data = retrieve_data("players")

    if username in playerbase_data["latest_stats"]:
        player_data = playerbase_data["latest_stats"][username]
    elif username in playerbase_data["unranked_stats"]:
        player_data = playerbase_data["unranked_stats"][username]
    else:
        return None

    embed = discord.Embed(
        title=username,
        color=int(RANK_COLORS[player_data["rank"]], 16),
        url="https://ch.tetr.io/u/"+username
    )

    embed.set_thumbnail(
        url="https://tetrio.team2xh.net/images/ranks/{}.png".format(
            player_data['rank']
        )
    )

    tr_string = f"{player_data['TR']:.0f}"

    # tenchi doesn't track unranked player rd
    if player_data["rank"] != "z":
        tr_string += f" ± {player_data['RD']}"

    def field(key: str, value: str, inline: bool = True):
        embed.add_field(name=key, value=value, inline=inline)

    field("Tetra Rating", tr_string, False)
    field("APM", player_data["apm"])
    field("PPS", player_data["pps"])
    field("VS", player_data["VS"])

    return embed


if __name__ == "__main__":
    retrieve_data("players")
