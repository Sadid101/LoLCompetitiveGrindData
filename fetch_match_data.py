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

index = 0
match_list = list(match_ids)
while index < len(match_list):
# while index < 98:
    
    matches_data = []
    selected_match_id = match_list[index]
    url = "https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
    response = requests.get(url.format(match_id=selected_match_id), headers=headers)
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
            header=(index == 0),
            index=False
        )

        print(f"Successfully fetched match {index + 1} of {len(match_list)}")
        index += 1
    elif response.status_code == 429:
        print("Rate limit hit. Waiting 120 seconds...")
        time.sleep(120)
    else:
        print(f"Failed to fetch match history for {selected_match_id}: {response.status_code}")
        print(f"Saving till index {index}, and match_id {selected_match_id}")
        break

print(f"Finished fetching match data. Total matches fetched: {index}")