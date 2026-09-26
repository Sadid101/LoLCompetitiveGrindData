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

players = pd.read_csv("players_with_match_history.csv")

match_ids = set()
total_matches = 0

for _, individual_player in players.iterrows():
    history = individual_player["match_history"]
    if pd.isna(history):
        continue

    for match_id in str(history).split(","):
        match_id = match_id.strip()

        if match_id:
            match_ids.add(match_id)
            total_matches += 1

print(
    f"Total unique match IDs: {len(match_ids)} "
    f"from {total_matches} total matches."
)
matches_data = []

index = 0
match_list = list(match_ids)
while index < len(match_list):
    selected_match_id = match_list[index]
    url = "https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url.format(match_id=selected_match_id), headers=headers)
    if response.status_code == 200:
        game_data = response.json()
        game_info = game_data["info"]
        matches_data.append({
            "match_id": selected_match_id,
            "game_info": game_info
        })
        print(f"Successfully fetched match history for index {index} of {len(match_list)}")
        index += 1
    elif response.status_code == 429:
        print("Rate limit hit. Waiting 120 seconds...")
        time.sleep(120)
    else:
        print(f"Failed to fetch match history for {selected_match_id}: {response.status_code}")
        index += 1 


df = pd.DataFrame(matches_data)
df.to_csv("match_data.csv", index=False)