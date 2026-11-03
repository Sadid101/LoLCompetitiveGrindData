import pandas as pd

players = pd.read_csv("players_with_match_history.csv")
matches = pd.read_csv("match_data.csv")

data = []
for player in players.itertuples():
    
    match_ids = str(player.match_history).split(",")

    player_matches = matches[
        matches["match_id"].isin(match_ids)
    ].copy()

    player_matches = player_matches.sort_values("game_creation")

    total_wins = len(player_matches[player_matches["win"] == True])
    avg_kills = player_matches["kills"].mean()
    avg_deaths = player_matches["deaths"].mean()
    avg_assists = player_matches["assists"].mean()
    avg_kda = (avg_kills + avg_assists) / (avg_deaths if avg_deaths != 0 else 1)
    avg_game_duration = player_matches["game_duration"].mean() / 60

    time_between_games = []
    time_after_win = []
    time_after_loss = []
    for i in range(len(player_matches) - 1):
        current_match = player_matches.iloc[i]
        next_match = player_matches.iloc[i + 1]

        minutes = (
            next_match["game_creation"] - current_match["game_end_timestamp"]
        ) / 60000

        if minutes >= 0:
            time_between_games.append(minutes)

            if current_match["win"]:
                time_after_win.append(minutes)
            else:
                time_after_loss.append(minutes)

    avg_time_between_games = sum(time_between_games) / len(time_between_games) if time_between_games else None
    avg_time_after_win = sum(time_after_win) / len(time_after_win) if time_after_win else None
    avg_time_after_loss = sum(time_after_loss) / len(time_after_loss) if time_after_loss else None


    data.append({
        "puuid": player.puuid,
        "tier": player.tier,
        "division": player.division,
        "leaguePoints": player.leaguePoints,
        "wins": player.wins,
        "losses": player.losses,
        "veteran": player.veteran,
        "inactive": player.inactive,
        "freshBlood": player.freshBlood,
        "hotStreak": player.hotStreak,
        "total_wins": total_wins,
        "avg_kda": avg_kda,
        "avg_game_duration": avg_game_duration,
        "avg_time_between_games": avg_time_between_games,
        "avg_time_after_win": avg_time_after_win,
        "avg_time_after_loss": avg_time_after_loss
    })
    print(f"Processed player {player.puuid} with {len(player_matches)} matches.")

df = pd.DataFrame(data)
df.to_csv("player_grind_data.csv", index=False)    