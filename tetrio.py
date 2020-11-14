import json
import os
from dataclasses import dataclass

import discord
import requests

TETRIO_CACHE = "tetrio_cache"
RANKS = {
    "z": {"value": -1, "color": "828282", "proper": "Unranked"},
    "d": {"value": 0, "color": "856C84", "proper": "D"},
    "dp": {"value": 1, "color": "815880", "proper": "D+"},
    "cm": {"value": 2, "color": "6C417C", "proper": "C-"},
    "c": {"value": 3, "color": "67287B", "proper": "C"},
    "cp": {"value": 4, "color": "522278", "proper": "C+"},
    "bm": {"value": 5, "color": "5949BE", "proper": "B-"},
    "b": {"value": 6, "color": "4357B5", "proper": "B"},
    "bp": {"value": 7, "color": "4880B2", "proper": "B+"},
    "am": {"value": 8, "color": "35AA8C", "proper": "A-"},
    "a": {"value": 9, "color": "3EA750", "proper": "A"},
    "ap": {"value": 10, "color": "43b536", "proper": "A+"},
    "sm": {"value": 11, "color": "B79E2B", "proper": "S-"},
    "s": {"value": 12, "color": "d19e26", "proper": "S"},
    "sp": {"value": 13, "color": "dbaf37", "proper": "S+"},
    "ss": {"value": 14, "color": "e39d3b", "proper": "SS"},
    "u": {"value": 15, "color": "c75c2e", "proper": "U"},
    "x": {"value": 16, "color": "b852bf", "proper": "X"},
}


def retrieve_data(endpoint: str, use_cache: bool = True, name: str = None):
    if not os.path.exists(TETRIO_CACHE):
        os.mkdir(TETRIO_CACHE)

    if name:
        cache_path = f"./{TETRIO_CACHE}/{name}.json"
    else:
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
class tetrio_user_data():
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
    highest_rank: str

    @staticmethod
    def from_username(username: str, playerbase_data, player_history_data):
        username = username.lower()
        latest_stats = playerbase_data["latest_stats"]
        unranked_stats = playerbase_data["unranked_stats"]

        if username in latest_stats:
            player_data = latest_stats[username]
        elif username in unranked_stats:
            player_data = unranked_stats[username]
        else:
            return None

        rank_history = player_history_data["ranks"][username]["rank"]
        largestIndex = max([
            [RANKS[r]["proper"].lower() for r in RANKS].index(rank)
            for rank in rank_history
        ])

        highest_rank = list(RANKS.keys())[largestIndex]

        return tetrio_user_data(
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
            games_lost=player_data["GL"],
            highest_rank=highest_rank
        )

    def generate_embed(self):
        embed = discord.Embed(
            title=self.username,
            color=int(RANKS[self.rank]["color"], 16),
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

    def to_row(self):
        return [
            self.tetra_rating,
            self.rank,
            self.apm,
            self.pps,
            self.vs,
            self.highest_rank
        ]


@dataclass
class tetrio_user():
    username: str
    current_stats: tetrio_user_data
    announcement_stats: tetrio_user_data

    current_playerbase_data = retrieve_data("players")
    current_player_history_data = retrieve_data("player_history")

    announcement_playerbase_data = retrieve_data(
        "players", True, "announcement")
    announcement_player_history_data = retrieve_data(
        "player_history", True, "announcement_history")

    @staticmethod
    def from_username(username: str):
        username = username.lower()
        return tetrio_user(
            username=username,
            current_stats=tetrio_user_data.from_username(
                username, tetrio_user.current_playerbase_data,
                tetrio_user.current_player_history_data),
            announcement_stats=tetrio_user_data.from_username(
                username, tetrio_user.announcement_playerbase_data,
                tetrio_user.announcement_player_history_data),
        )

    def to_row(self) -> list:
        return [self.username] + self.current_stats.to_row() + \
            self.announcement_stats.to_row()


if __name__ == "__main__":
    retrieve_data("players", False, "announcement")
    retrieve_data("player_history", False, "announcement_history")
