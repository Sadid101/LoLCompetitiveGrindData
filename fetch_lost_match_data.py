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

# Load player match histories
players = pd.read_csv("players_with_match_history.csv")

# Load existing match data
existing_matches = pd.read_csv("match_data.csv")

# Get all match IDs from player data
player_match_ids = set()

for _, individual_player in players.iterrows():
    history = individual_player["match_history"]

    if pd.isna(history):
        continue

    for match_id in str(history).split(","):
        match_id = match_id.strip()

        if match_id:
            player_match_ids.add(match_id)

# Get match IDs already collected
collected_match_ids = set(existing_matches["match_id"].astype(str))

# Find missing match IDs
missing_match_ids = player_match_ids - collected_match_ids

print(f"Total unique player match IDs: {len(player_match_ids)}")
print(f"Already collected: {len(collected_match_ids)}")
print(f"Missing matches to fetch: {len(missing_match_ids)}")

# Fetch only missing matches
match_list = list(missing_match_ids)

index = 0

while index < len(match_list):

    matches_data = []
    selected_match_id = match_list[index]

    url = "https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"

    response = requests.get(
        url.format(match_id=selected_match_id),
        headers=headers
    )

    if response.status_code == 200:

        game_data = response.json()
        game_info = game_data["info"]
        participants = game_info["participants"]

        for participant in participants:
            matches_data.append({
                "match_id": selected_match_id,
                "game_id": game_info["gameId"],
                "game_creation": game_info["gameCreation"],
                "game_duration": game_info["gameDuration"],
                "game_end_timestamp": game_info["gameEndTimestamp"],

                "team_id": participant["teamId"],
                "puuid": participant["puuid"],
                "champion": participant["championName"],
                "win": participant["win"],
                "kills": participant["kills"],
                "deaths": participant["deaths"],
                "assists": participant["assists"],
                "riot_id": participant.get("riotIdGameName"),
                "riot_tag": participant.get("riotIdTagline"),
                "summoner_id": participant["summonerId"],
                "was_afk": participant.get("wasAfk"),

                "nexus_lost": participant.get("nexusLost"),
                "position_assigned_by_matchmaking": participant.get("positionAssignedByMatchmaking"),
                "team_position": participant.get("teamPosition"),
                "selected_role_preference": participant.get("selectedRolePreferences"),

                "was_premade_with_ign_game_end_causer": participant.get("wasPremadeWithIGNBGameEndCauser"),
                "was_premade_with_severe_transgressor": participant.get("wasPremadeWithSevereTransgressor"),
                "was_severe_transgressor": participant.get("wasSevereTransgressor"),
                "eligible_for_progression": participant.get("eligibleForProgression"),
            })

        pd.DataFrame(matches_data).to_csv(
            "match_data.csv",
            mode="a",
            header=False,
            index=False
        )

        print(f"Successfully fetched missing match {index + 1} of {len(match_list)}")

        index += 1

    elif response.status_code == 429:
        print("Rate limit hit. Waiting 120 seconds...")
        time.sleep(120)

    else:
        print(f"Failed to fetch match {selected_match_id}: {response.status_code}")
        print(f"Stopping at index {index}")
        break

print(f"Finished. Total missing matches fetched: {index}")