import streamlit as st
import pandas as pd

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------
st.set_page_config(page_title="Team Dashboard", layout="wide")
st.title("🏀 Team Analytics Dashboard")
st.caption("Season Team Overview")

# --------------------------------------------------
# LOAD & CLEAN DATA
# --------------------------------------------------
df = pd.read_csv("data/player_box_scores.csv")

numeric_cols = [
    "fgm", "fga", "tpm", "tpa", "ftm", "fta",
    "oreb", "dreb", "ast", "stl", "blk",
    "tov", "foul", "pts"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

df["reb"] = df["oreb"] + df["dreb"]

# --------------------------------------------------
# TEAM TOTALS PER GAME
# --------------------------------------------------
team_games = (
    df.groupby(
        ["game_id", "date", "opponent", "location"],
        as_index=False
    )
    .agg({
        "pts": "sum",
        "fgm": "sum",
        "fga": "sum",
        "tpm": "sum",
        "tpa": "sum",
        "oreb": "sum",
        "dreb": "sum",
        "ast": "sum",
        "tov": "sum"
    })
)

team_games["date"] = pd.to_datetime(team_games["date"])

# Create readable game label (prevents opponent merging)
team_games["game_label"] = (
    team_games["date"].dt.strftime("%m/%d")
    + " "
    + team_games["location"].map({"H": "vs", "A": "@"}).fillna("vs")
    + " "
    + team_games["opponent"]
)

games_played = len(team_games)

# --------------------------------------------------
# PER-GAME METRICS
# --------------------------------------------------
ppg = team_games["pts"].mean()
oreb_pg = team_games["oreb"].mean()
dreb_pg = team_games["dreb"].mean()
ast_pg = team_games["ast"].mean()
tov_pg = team_games["tov"].mean()
fga_pg = team_games["fga"].mean()
tpa_pg = team_games["tpa"].mean()

fg_pct = team_games["fgm"].sum() / team_games["fga"].sum()
tp_pct = team_games["tpm"].sum() / team_games["tpa"].sum()

# --------------------------------------------------
# METRICS DISPLAY
# --------------------------------------------------
st.subheader("📊 Team Per-Game Profile")

row1 = st.columns(5)
row1[0].metric("PPG", round(ppg, 1))
row1[1].metric("OREB / G", round(oreb_pg, 1))
row1[2].metric("DREB / G", round(dreb_pg, 1))
row1[3].metric("AST / G", round(ast_pg, 1))
row1[4].metric("TOV / G", round(tov_pg, 1))

row2 = st.columns(5)
row2[0].metric("FG%", f"{fg_pct:.1%}")
row2[1].metric("3PT FG%", f"{tp_pct:.1%}")
row2[2].metric("FGA / G", round(fga_pg, 1))
row2[3].metric("3PA / G", round(tpa_pg, 1))
row2[4].metric("Games", games_played)

# --------------------------------------------------
# GAME FILTER
# --------------------------------------------------
st.subheader("📅 Game Filter")

last_n = st.slider(
    "Show last N games",
    min_value=1,
    max_value=games_played,
    value=games_played
)

filtered_games = (
    team_games
    .sort_values("date")
    .tail(last_n)
)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------
st.subheader("📈 Performance by Game")

# Points by Game
st.markdown("**Points Scored**")
st.bar_chart(
    filtered_games.set_index("game_label")["pts"]
)

# Turnovers by Game
st.markdown("**Turnovers**")
st.bar_chart(
    filtered_games.set_index("game_label")["tov"]
)

# Rebounds by Game
st.markdown("**Rebounds (Offensive / Defensive)**")
st.bar_chart(
    filtered_games.set_index("game_label")[["oreb", "dreb"]]
)

# Shot Volume Trend
st.subheader("🎯 Shot Volume Trend")
st.line_chart(
    filtered_games.set_index("game_label")[["fga", "tpa"]]
)
