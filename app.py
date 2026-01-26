import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="JV Basketball – Team Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("all_games_master.csv", parse_dates=["game_date"])

df = load_data()

# ---------------- BASIC CALCS ----------------
df["reb"] = df.get("oreb", 0) + df.get("dreb", 0)
played_df = df[~df["dnp"]]  # exclude DNPs for per-player stats

# ---------------- PLAYER PER-GAME STATS ----------------
games_played = played_df.groupby("player")["game_date"].nunique()
player_totals = played_df.groupby("player").sum(numeric_only=True)

# Calculate per-game stats
player_per_game = pd.DataFrame({
    "GP": games_played,
    "PPG": (player_totals["pts"] / games_played).round(1),
    "RPG": (player_totals["reb"] / games_played).round(1),
    "APG": (player_totals["asst"] / games_played).round(1),
    "SPG": (player_totals["stl"] / games_played).round(1),
    "BPG": (player_totals["blk"] / games_played).round(1),
    "TOPG": (player_totals["to"] / games_played).round(1),
    "FG%": (player_totals["fgm"] / player_totals["fga"]),
    "3PT%": (player_totals["3pm"] / player_totals["3pa"]),
    "FT%": (player_totals["ftm"] / player_totals["fta"]),
})

player_per_game = player_per_game.sort_values("PPG", ascending=False)

# Pre-format numbers for display (strings) to force 1 decimal
def format_number(val):
    return f"{val:.1f}"

def format_percent(val):
    return f"{val*100:.1f}%"

player_per_game_display = player_per_game.copy()
for col in ["PPG", "RPG", "APG", "SPG", "BPG", "TOPG", "GP"]:
    player_per_game_display[col] = player_per_game_display[col].apply(format_number)

for col in ["FG%", "3PT%", "FT%"]:
    player_per_game_display[col] = player_per_game_display[col].apply(format_percent)

# ---------------- TEAM PER-GAME STATS ----------------
team_games = df["game_date"].nunique()
team_per_game = pd.DataFrame({
    "PTS/G": round(df["pts"].sum() / team_games, 1),
    "REB/G": round(df["reb"].sum() / team_games, 1),
    "AST/G": round(df["asst"].sum() / team_games, 1),
    "STL/G": round(df["stl"].sum() / team_games, 1),
    "BLK/G": round(df["blk"].sum() / team_games, 1),
    "TO/G": round(df["to"].sum() / team_games, 1),
    "FG%": df["fgm"].sum() / df["fga"].sum(),
    "3PT%": df["3pm"].sum() / df["3pa"].sum(),
    "FT%": df["ftm"].sum() / df["fta"].sum(),
}, index=["Team"])

team_per_game_display = team_per_game.copy()
for col in ["PTS/G", "REB/G", "AST/G", "STL/G", "BLK/G", "TO/G"]:
    team_per_game_display[col] = team_per_game_display[col].apply(format_number)
for col in ["FG%", "3PT%", "FT%"]:
    team_per_game_display[col] = team_per_game_display[col].apply(format_percent)

# ---------------- HEADER ----------------
st.title("JV Basketball – Team Dashboard")

# ---------------- PLAYER TABLE ----------------
st.subheader("Player Per-Game Averages")
st.dataframe(player_per_game_display)

# ---------------- TEAM TABLE ----------------
st.subheader("Team Per-Game Stats")
st.dataframe(team_per_game_display)

# ---------------- ALL PLAYERS CHART ----------------
# st.subheader("All Players – Points Per Game")

# per_game = df.groupby(["player", "game_date"], as_index=False).sum(numeric_only=True)
# per_game["player_avg"] = per_game.groupby("player")["pts"].transform("mean")

# # Round points for chart
# per_game["pts"] = per_game["pts"].round(1)
# per_game["player_avg"] = per_game["player_avg"].round(1)

# chart = alt.Chart(per_game).mark_line(point=True).encode(
# x=alt.X("game_date:T", title="Game"),
# y=alt.Y("pts:Q", title="Points"),
# color=alt.Color("player:N", title="Player"),
# tooltip=["player", "pts"]
# ).properties(height=400)

# avg_lines = alt.Chart(
# per_game.groupby("player", as_index=False)["player_avg"].mean()
# ).mark_rule(strokeDash=[4, 4]).encode(
# y="player_avg:Q",
# color="player:N"
# )

# st.altair_chart(chart + avg_lines, width='stretch')
