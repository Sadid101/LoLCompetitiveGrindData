import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
headers = {
    "X-Riot-Token": API_KEY
}

players = pd.read_csv("players.csv")

matches = []

index = 0

while index < len(players):
    player = players.iloc[index]
    player_puuid = player["puuid"]
    url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    response = requests.get(url.format(puuid=player_puuid), headers=headers, params={"count": 10})
    if response.status_code == 200:
        match_ids = response.json()
        players.at[index, "match_history"] = ",".join(match_ids)
        print(f"Successfully fetched match history for player {player_puuid}")
        index += 1
    elif response.status_code == 429:
        print("Rate limit hit. Waiting 120 seconds...")
        time.sleep(120)
    else:
        print(f"Failed to fetch match history for {player_puuid}: {response.status_code}")
        index += 1 


df = pd.DataFrame(players)
df.to_csv("players_with_match_history.csv", index=False)