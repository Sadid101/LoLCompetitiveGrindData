import os
import time
import requests
import pandas as pd
import random
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
headers = {
    "X-Riot-Token": API_KEY
}



players = []


def fetch_match_history(puuid):
    url = "https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
    response = requests.get(url.format(puuid=puuid), headers=headers, params={"count": 10})
    if response.status_code == 200:
        print("Successfully fetched match history data")
        return response.json()
    elif response.status_code == 429:
        print("Rate limit hit. Waiting 120 seconds...")
        time.sleep(120)
        return fetch_match_history(puuid)
    else:
        print(f"Failed to fetch match history for {puuid}: {response.status_code}")
        return []


def fetch_players():

    tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "EMERALD", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
    divisions = ["I", "II", "III", "IV"]
    url = "https://euw1.api.riotgames.com/lol/league-exp/v4/entries/RANKED_SOLO_5x5/{tier}/{division}?page={page}"
    for tier in tiers:
        possible_divisions = divisions if tier not in ["MASTER", "GRANDMASTER", "CHALLENGER"] else ["I"]
        for division in possible_divisions:
            # randomPages = random.sample(range(1, 6), 1)
            # for page in randomPages:
            response = requests.get(url.format(tier=tier, division=division, page=1), headers=headers)
            if response.status_code == 200:
                data = response.json()
                randomPlayers = random.sample(data, min(100, len(data)))
                for player in data:
                    match_history = fetch_match_history(player["puuid"])
                    players.append({
                        "puuid": player["puuid"],
                        "match_history": match_history,
                        "tier": tier,
                        "division": division,
                        "leaguePoints": player["leaguePoints"],
                        "wins": player["wins"],
                        "losses": player["losses"],
                        "veteran": player["veteran"],
                        "inactive": player["inactive"],
                        "freshBlood": player["freshBlood"],
                        "hotStreak": player["hotStreak"]
                    })
            else:
                print(f"Failed to fetch data for {tier} {division} page {1}: {response.status_code}")


fetch_players();

df = pd.DataFrame(players)
df.to_csv("players.csv", index=False)

# "rank": "I",
# "puuid": "cV3cicdkqlJ9aU1lWxevfM5bcR71h--A8OkTt3qbIKmEg3R0gW2v-W1nmWxAyNi_khiIJn4EcxFrGw",
# "leaguePoints": 2466,
# "wins": 486,
# "losses": 386,
# "veteran": true,
# "inactive": false,
# "freshBlood": false,
# "hotStreak": false