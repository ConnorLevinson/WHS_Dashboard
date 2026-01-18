import streamlit as st
import pandas as pd

st.set_page_config(page_title="Team Dashboard", layout="wide")
st.title("🏀 Team Dashboard")

# Load data
df = pd.read_csv("data/player_box_scores.csv")

# Numeric columns we actually have
numeric_cols = [
    "fgm", "fga", "tpm", "tpa", "ftm", "fta",
    "oreb", "dreb",
    "ast", "stl", "blk", "tov", "foul", "pts"
]

# Force numeric (handles blanks / spaces)
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# Derived stats
df["reb"] = df["oreb"] + df["dreb"]

# Team overview
games_played = df["game_id"].nunique()
total_points = df["pts"].sum()
ppg = total_points / games_played if games_played > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Games Played", games_played)
col2.metric("Total Points", int(total_points))
col3.metric("Points Per Game", round(ppg, 1))

# Team totals per game
team_games = (
    df.groupby("game_id")[["opponent","pts", "reb", "ast", "tov"]]
    .sum()
    .reset_index()
)

st.subheader("Team Points by Game")
st.line_chart(team_games.set_index("opponent")["pts"])

st.subheader("Team Rebounds by Game")
st.line_chart(team_games.set_index("opponent")["reb"])
