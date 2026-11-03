import pandas as pd

players = pd.read_csv("players_with_match_history.csv")
matches = pd.read_csv("match_data.csv")

data = []
for player in players.itertuples():
    
    match_ids = str(player.match_history).split(",")

    player_matches = matches[
        (matches["match_id"].isin(match_ids)) &
        (matches["puuid"] == player.puuid)
    ].copy()


    #general calculations
    player_matches = player_matches.sort_values("game_creation")

    wins_in_match_data = len(player_matches[player_matches["win"] == True])
    avg_kills = player_matches["kills"].mean()
    avg_deaths = player_matches["deaths"].mean()
    avg_assists = player_matches["assists"].mean()
    avg_game_duration = player_matches["game_duration"].mean() / 60



    # All participants in the player's match history
    player_match_data = matches[
        matches["match_id"].isin(match_ids)
    ].copy()

    # Find the player's team in each match
    player_teams = player_match_data[
        player_match_data["puuid"] == player.puuid
    ][["match_id", "team_id"]].drop_duplicates()

    # Find teammates
    teammates = player_match_data.merge(
        player_teams,
        on=["match_id", "team_id"]
    )

    teammates = teammates[teammates["puuid"] != player.puuid]

    # Count repeated teammates
    teammate_counts = teammates.groupby("puuid")["match_id"].nunique()

    repeated_teammates = teammate_counts[teammate_counts >= 3]
    has_premade = len(repeated_teammates) > 0



    #match specific calculations
    time_between_games = []
    time_after_win = []
    time_after_loss = []
    time_after_3_wins = []
    time_after_3_losses = []

    sessions = []
    current_session = []

    for i in range(len(player_matches)):
        current_match = player_matches.iloc[i]

        # Check whether a new session starts
        if i > 0:
            previous_match = player_matches.iloc[i - 1]

            break_minutes = (
                current_match["game_creation"] - previous_match["game_end_timestamp"]
            ) / 60000

            if break_minutes > 30:
                sessions.append(current_session)
                current_session = []

        current_session.append(current_match)

        # Calculate time until the next game
        if i < len(player_matches) - 1:
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

            # Check for 3+ consecutive wins/losses
            if i >= 2:
                previous_three = player_matches.iloc[i-2:i+1]

                if minutes >= 0:
                    if all(previous_three["win"] == True):
                        time_after_3_wins.append(minutes)
                    elif all(previous_three["win"] == False):
                        time_after_3_losses.append(minutes)

    # Append the final session
    if current_session:
        sessions.append(current_session)

    # Time averages
    avg_time_between_games = sum(time_between_games) / len(time_between_games) if time_between_games else -1
    avg_time_after_win = sum(time_after_win) / len(time_after_win) if time_after_win else -1
    avg_time_after_loss = sum(time_after_loss) / len(time_after_loss) if time_after_loss else -1

    avg_time_after_3_wins = sum(time_after_3_wins) / len(time_after_3_wins) if time_after_3_wins else -1
    avg_time_after_3_losses = sum(time_after_3_losses) / len(time_after_3_losses) if time_after_3_losses else -1

    # Session statistics
    session_wins = [sum(match["win"] for match in session) for session in sessions]
    session_losses = [len(session) - wins for session, wins in zip(sessions, session_wins)]
    session_games = [len(session) for session in sessions]

    total_sessions = len(sessions)
    avg_session_wins = sum(session_wins) / total_sessions if total_sessions else -1
    avg_session_losses = sum(session_losses) / total_sessions if total_sessions else -1
    avg_games_per_session = sum(session_games) / total_sessions if total_sessions else -1
    longest_session = max(session_games) if session_games else -1

    win_rate = wins_in_match_data / len(player_matches) if len(player_matches) > 0 else -1

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
        "avg_game_duration": avg_game_duration,
        "avg_time_between_games": avg_time_between_games,
        "avg_time_after_win": avg_time_after_win,
        "avg_time_after_loss": avg_time_after_loss,
        "avg_kills": avg_kills,
        "avg_deaths": avg_deaths,
        "avg_assists": avg_assists,
        "has_premade": has_premade,
        "total_matches": len(player_matches),
        "total_sessions": total_sessions,
        "wins_in_match_data": wins_in_match_data,
        "win_rate_in_match_data": win_rate,
        "avg_session_wins": avg_session_wins,
        "avg_session_losses": avg_session_losses,
        "avg_games_per_session": avg_games_per_session,
        "longest_session": longest_session,
        "avg_time_after_3_wins": avg_time_after_3_wins,
        "avg_time_after_3_losses": avg_time_after_3_losses
    })
    print(f"Processed player {player.puuid} with {len(player_matches)} matches.")

df = pd.DataFrame(data)
df.to_csv("player_grind_data.csv", index=False)    