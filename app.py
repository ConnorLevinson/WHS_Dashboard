import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="JV Basketball – Team Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("all_games_master.csv", parse_dates=["game_date"])

@st.cache_data
def load_opp_data():
    return pd.read_csv("opponent_stats.csv", parse_dates=["game_date"])

df = load_data()
opp_df = load_opp_data()

# Merge opponent stats
df = df.merge(
    opp_df,
    on=["game_date", "location", "opponent"],
    how="left"
)

# ---------------- BASIC CALCS ----------------
df["reb"] = df["oreb"] + df["dreb"]

# Team & opponent points per game
team_pts = df.groupby("game_date")["pts"].transform("sum")
opp_pts = (
    df["opp_fgm"] * 2 +
    df["opp_3pm"] +
    df["opp_ftm"]
)

# Explicit game result
df["result"] = "L"
df.loc[team_pts > opp_pts, "result"] = "W"
df.loc[team_pts == opp_pts, "result"] = "T"

# Win flag for stats (ties count as losses)
df["win_for_stats"] = df["result"] == "W"

played_df = df[~df["dnp"]]

# ---------------- RECORD ----------------
record_df = df[["game_date", "result"]].drop_duplicates()

wins = (record_df["result"] == "W").sum()
losses = (record_df["result"] == "L").sum()
ties = (record_df["result"] == "T").sum()

# ---------------- TEAM PER-GAME ----------------
games = df["game_date"].nunique()

team_pg = pd.DataFrame({
    "PTS/G": df["pts"].sum() / games,
    "REB/G": df["reb"].sum() / games,
    "AST/G": df["asst"].sum() / games,
    "STL/G": df["stl"].sum() / games,
    "BLK/G": df["blk"].sum() / games,
    "TO/G": df["to"].sum() / games,
    "FG%": df["fgm"].sum() / df["fga"].sum(),
    "3PT%": df["3pm"].sum() / df["3pa"].sum(),
    "FT%": df["ftm"].sum() / df["fta"].sum()
}, index=["Team"])

# ---------------- TEAM WINS vs LOSSES ----------------
team_game = (
    df
    .groupby(["game_date", "win_for_stats"])
    .agg({
        "pts": "sum",
        "reb": "sum",
        "asst": "sum",
        "to": "sum",
        "fgm": "sum",
        "fga": "sum",
        "3pm": "sum",
        "3pa": "sum",
        "ftm": "sum",
        "fta": "sum"
    })
    .reset_index()
)

team_game["FG%"] = team_game["fgm"] / team_game["fga"]
team_game["3PT%"] = team_game["3pm"] / team_game["3pa"]
team_game["FT%"] = team_game["ftm"] / team_game["fta"]

wl_team = (
    team_game
    .groupby("win_for_stats")
    .mean(numeric_only=True)
    .rename(index={True: "Wins", False: "Losses (incl. Ties)"})
)

# ---------------- OPPONENT WINS vs LOSSES (PER GAME) ----------------
opp_game = (
    df
    .groupby(["game_date", "win_for_stats"])
    .agg({
        "opp_fgm": "first",
        "opp_fga": "first",
        "opp_3pm": "first",
        "opp_3pa": "first",
        "opp_ftm": "first",
        "opp_fta": "first",
        "opp_reb": "first",
        "opp_to": "first"
    })
    .reset_index()
)

opp_game["Opp PTS"] = (
    opp_game["opp_fgm"] * 2 +
    opp_game["opp_3pm"] +
    opp_game["opp_ftm"]
)

opp_game["Opp FG%"] = opp_game["opp_fgm"] / opp_game["opp_fga"]
opp_game["Opp 3PT%"] = opp_game["opp_3pm"] / opp_game["opp_3pa"]
opp_game["Opp FT%"] = opp_game["opp_ftm"] / opp_game["opp_fta"]

wl_opp = (
    opp_game
    .groupby("win_for_stats")
    .mean(numeric_only=True)
    .rename(index={True: "Wins", False: "Losses (incl. Ties)"})
)

# ---------------- PLAYER PER-GAME ----------------
games_played = played_df.groupby("player")["game_date"].nunique()
player_totals = played_df.groupby("player").sum(numeric_only=True)

player_pg = pd.DataFrame({
    "GP": games_played,
    "PPG": player_totals["pts"] / games_played,
    "RPG": player_totals["reb"] / games_played,
    "APG": player_totals["asst"] / games_played,
    "SPG": player_totals["stl"] / games_played,
    "BPG": player_totals["blk"] / games_played,
    "TOPG": player_totals["to"] / games_played,
    "FG%": player_totals["fgm"] / player_totals["fga"],
    "3PT%": player_totals["3pm"] / player_totals["3pa"],
    "FT%": player_totals["ftm"] / player_totals["fta"]
}).sort_values("PPG", ascending=False)

# ---------------- PAGE ----------------
st.title("JV Basketball – Team Dashboard")
st.subheader(f"Team Record: {wins}-{losses}-{ties}")

st.subheader("Team Per-Game Stats")
st.dataframe(
    team_pg.style
    .format("{:.1f}", subset=team_pg.columns[:-3])
    .format("{:.1%}", subset=["FG%", "3PT%", "FT%"])
)

st.subheader("Team Stats — Wins vs Losses")
st.dataframe(
    wl_team[["pts","reb","asst","to","FG%","3PT%","FT%"]]
    .rename(columns={
        "pts":"PTS/G",
        "reb":"REB/G",
        "asst":"AST/G",
        "to":"TO/G"
    })
    .style
    .format("{:.1f}", subset=["PTS/G","REB/G","AST/G","TO/G"])
    .format("{:.1%}", subset=["FG%","3PT%","FT%"])
)

st.subheader("Opponent Stats — Wins vs Losses")
st.dataframe(
    wl_opp[["Opp PTS","opp_reb","opp_to","Opp FG%","Opp 3PT%","Opp FT%"]]
    .rename(columns={
        "Opp PTS":"Opp PTS/G",
        "opp_reb":"Opp REB/G",
        "opp_to":"Opp TO/G"
    })
    .style
    .format("{:.1f}", subset=["Opp PTS/G","Opp REB/G","Opp TO/G"])
    .format("{:.1%}", subset=["Opp FG%","Opp 3PT%","Opp FT%"])
)

st.subheader("Player Per-Game Averages")
st.dataframe(
    player_pg.style
    .format("{:.1f}", subset=player_pg.columns[:7])
    .format("{:.1%}", subset=["FG%","3PT%","FT%"])
)

# ---------------- GAME LOG ----------------
game_log_df = (
    df
    .groupby(["game_date", "opponent", "location"])
    .agg({
        # Team stats
        "pts": "sum",
        "reb": "sum",
        "asst": "sum",
        "stl": "sum",
        "blk": "sum",
        "to": "sum",
        "fgm": "sum",
        "fga": "sum",
        "3pm": "sum",
        "3pa": "sum",
        "ftm": "sum",
        "fta": "sum",
        # Opponent stats
        "opp_fgm": "first",
        "opp_fga": "first",
        "opp_3pm": "first",
        "opp_3pa": "first",
        "opp_ftm": "first",
        "opp_fta": "first",
        "opp_reb": "first",
        "opp_to": "first",
        # Result
        "result": "first"
    })
    .reset_index()
)

# Team shooting percentages
game_log_df["FG%"] = game_log_df["fgm"] / game_log_df["fga"]
game_log_df["3PT%"] = game_log_df["3pm"] / game_log_df["3pa"]
game_log_df["FT%"] = game_log_df["ftm"] / game_log_df["fta"]

# Opponent points
game_log_df["Opp PTS"] = (
    game_log_df["opp_fgm"] * 2 +
    game_log_df["opp_3pm"] +
    game_log_df["opp_ftm"]
)
game_log_df["Opp FG%"] = game_log_df["opp_fgm"] / game_log_df["opp_fga"]
game_log_df["Opp 3PT%"] = game_log_df["opp_3pm"] / game_log_df["opp_3pa"]
game_log_df["Opp FT%"] = game_log_df["opp_ftm"] / game_log_df["opp_fta"]

# Optional: reorder columns for readability
game_log_df = game_log_df[[
    "opponent", "location", "result",
    "pts", "reb", "asst", "stl", "blk", "to", "FG%", "3PT%", "FT%",
    "Opp PTS", "opp_reb", "opp_to", "Opp FG%", "Opp 3PT%", "Opp FT%"
]]

game_log_df = game_log_df[::-1]
game_log_df.index +=1
# ---------------- DISPLAY IN STREAMLIT ----------------
st.subheader("Game Log — Team vs Opponent Stats")
st.dataframe(
    game_log_df.style
    .format("{:.1f}", subset=["pts","reb","asst","stl","blk","to","opp_reb","opp_to","Opp PTS"])
    .format("{:.1%}", subset=["FG%","3PT%","FT%","Opp FG%","Opp 3PT%","Opp FT%"])
)
