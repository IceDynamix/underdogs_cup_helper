from dataclasses import dataclass
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


@dataclass
class tetrio_user():
    username: str
    tetra_rating: float
    rank: str
    rating_deviation: float
    glicko: float
    apm: float
    pps: float
    vs: float
    games_played: int
    games_won: int
    games_lost: int

    playerbase_data = retrieve_data("players")

    @staticmethod
    def from_username(username: str):
        username = username.lower()
        latest_stats = tetrio_user.playerbase_data["latest_stats"]
        unranked_stats = tetrio_user.playerbase_data["unranked_stats"]

        if username in latest_stats:
            player_data = latest_stats[username]
        elif username in unranked_stats:
            player_data = unranked_stats[username]
        else:
            return None

        return tetrio_user(
            username=username,
            tetra_rating=player_data["TR"],
            rank=player_data["rank"],
            rating_deviation=player_data["RD"],
            glicko=player_data["glk"],
            apm=player_data["apm"],
            pps=player_data["pps"],
            vs=player_data["VS"],
            games_played=player_data["GP"],
            games_won=player_data["GW"],
            games_lost=player_data["GL"]
        )

    def generate_embed(self):
        embed = discord.Embed(
            title=self.username,
            color=int(RANK_COLORS[self.rank], 16),
            url="https://ch.tetr.io/u/"+self.username
        )

        embed.set_thumbnail(
            url=f"https://tetrio.team2xh.net/images/ranks/{self.rank}.png"
        )

        tr_string = f"{self.tetra_rating:.0f}"

        # tenchi doesn't track unranked player rd
        if self.rank != "z":
            tr_string += f" ± {self.rating_deviation}"

        def field(key: str, value: str, inline: bool = True):
            embed.add_field(name=key, value=value, inline=inline)

        field("Tetra Rating", tr_string, False)
        field("APM", self.apm)
        field("PPS", self.pps)
        field("VS", self.vs)

        return embed
