import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt


st.set_page_config(page_title="JV Basketball – Team Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("all_games_master.csv", parse_dates=["game_date"])

df = load_data()

@st.cache_data
def load_opponent_data():
    return pd.read_csv(
        "opponent_stats.csv",
        parse_dates=["game_date"]
    )

opp_df = load_opponent_data()

df = df.merge(
    opp_df,
    on=["game_date", "location", "opponent"],
    how="left"
)

# ---------------- BASIC CALCS ----------------
df["reb"] = df.get("oreb", 0) + df.get("dreb", 0)
played_df = df[~df["dnp"]]  # exclude DNPs for per-player stats

# ---------------- PLAYER PER-GAME STATS ----------------
games_played = played_df.groupby("player")["game_date"].nunique()
player_totals = played_df.groupby("player").sum(numeric_only=True)

def vps_calculation(df):
    missed_fg = df["fga"] - df["fgm"]
    missed_ft = df["fta"] - df["ftm"]
    turnovers = df["to"]

    numerator = (
        df["pts"] +
        df["reb"] +
        2 * (df["stl"] + df["blk"] + df["asst"])
    )

    denominator = (
        2 * missed_fg +
        missed_ft +
        2 * turnovers
    )

    vps = numerator / denominator.replace(0, pd.NA)
    return vps

def efg_calculation(df):
    return (df["fgm"] + 0.5 * df["3pm"]) / df["fga"].replace(0, pd.NA)

def ts_calculation(df):
    return df["pts"] / (2 * (df["fga"] + 0.44 * df["fta"]).replace(0, pd.NA))

def to_rate_calculation(df):
    return df["to"] / (df["fga"] + 0.44 * df["fta"] + df["to"]).replace(0, pd.NA)

def efficiency_calculation(df):
    return (
        df["pts"]
        + df["reb"]
        + df["asst"]
        + df["stl"]
        + df["blk"]
        - (df["fga"] - df["fgm"])
        - (df["fta"] - df["ftm"])
        - df["to"]
    )


player_per_game = pd.DataFrame({
    "GP": games_played,
    "PPG": (player_totals["pts"] / games_played).round(1),
    "RPG": (player_totals["reb"] / games_played).round(1),
    "APG": (player_totals["asst"] / games_played).round(1),
    "SPG": (player_totals["stl"] / games_played).round(1),
    "BPG": (player_totals["blk"] / games_played).round(1),
    "TOPG": (player_totals["to"] / games_played).round(1),
    "FG%": player_totals["fgm"] / player_totals["fga"],
    "3PT%": player_totals["3pm"] / player_totals["3pa"],
    "FT%": player_totals["ftm"] / player_totals["fta"],
    "VPS": vps_calculation(player_totals),
    "eFG%": efg_calculation(player_totals),
    "TS%": ts_calculation(player_totals),
    "TO Rate": to_rate_calculation(player_totals),
    "EFF": efficiency_calculation(player_totals) / games_played

}).sort_values("PPG", ascending=False)

# ---------------- FORMAT HELPERS ----------------
def format_number(val):
    return f"{val:.1f}"

def format_percent(val):
    return f"{val*100:.1f}%"

player_per_game_display = player_per_game.copy()

for col in ["PPG", "RPG", "APG", "SPG", "BPG", "TOPG", "GP", "VPS", "EFF"]:
    player_per_game_display[col] = player_per_game_display[col].apply(format_number)

for col in ["FG%", "3PT%", "FT%", "eFG%", "TS%", "TO Rate"]:
    player_per_game_display[col] = player_per_game_display[col].apply(format_percent)

# ---------------- TEAM PER-GAME STATS ----------------
team_games = df["game_date"].nunique()

team_per_game = pd.DataFrame({
    "PTS/G": df["pts"].sum() / team_games,
    "REB/G": df["reb"].sum() / team_games,
    "AST/G": df["asst"].sum() / team_games,
    "STL/G": df["stl"].sum() / team_games,
    "BLK/G": df["blk"].sum() / team_games,
    "TO/G": df["to"].sum() / team_games,
    "FG%": df["fgm"].sum() / df["fga"].sum(),
    "3PT%": df["3pm"].sum() / df["3pa"].sum(),
    "FT%": df["ftm"].sum() / df["fta"].sum(),
}, index=["Team"])

team_per_game_display = team_per_game.copy()

for col in ["PTS/G", "REB/G", "AST/G", "STL/G", "BLK/G", "TO/G"]:
    team_per_game_display[col] = team_per_game_display[col].apply(format_number)

for col in ["FG%", "3PT%", "FT%"]:
    team_per_game_display[col] = team_per_game_display[col].apply(format_percent)

# Add 🔑 to key headers
team_per_game_display.rename(columns={"REB/G": "REB/G 🔑", "TO/G": "TO/G 🔑"}, inplace=True)

# ---------------- OPPONENT PER-GAME STATS ----------------

games = opp_df["game_date"].nunique()

opp_pg = pd.DataFrame({
    "Opp PTS/G": round(
        (opp_df["opp_fgm"].sum() * 2 + opp_df["opp_3pm"].sum() + opp_df["opp_ftm"].sum()) / games, 1
    ),
    "Opp REB/G": round(opp_df["opp_reb"].sum() / games, 1),
    "Opp TO/G": round(opp_df["opp_to"].sum() / games, 1),
    "Opp FG%": opp_df["opp_fgm"].sum() / opp_df["opp_fga"].sum(),
    "Opp 3PT%": opp_df["opp_3pm"].sum() / opp_df["opp_3pa"].sum(),
    "Opp FT%": opp_df["opp_ftm"].sum() / opp_df["opp_fta"].sum(),
}, index=["Opponent"])

opp_pg_display = opp_pg.copy()

for col in ["Opp PTS/G", "Opp REB/G", "Opp TO/G"]:
    opp_pg_display[col] = opp_pg_display[col].apply(format_number)

for col in ["Opp FG%", "Opp 3PT%", "Opp FT%"]:
    opp_pg_display[col] = opp_pg_display[col].apply(format_percent)

# Add 🔑 to opponent key headers
opp_pg_display.rename(columns={"Opp REB/G": "Opp REB/G 🔑", "Opp TO/G": "Opp TO/G 🔑"}, inplace=True)

# ---------------- SHOT DISTRIBUTION PIE (MATPLOTLIB – RELIABLE) ----------------

TOP_N = 10  # number of players to show individually

shot_df = (
    played_df
    .groupby("player", as_index=False)[["fgm", "fga"]]
    .sum()
    .sort_values("fga", ascending=False)
)

top = shot_df.head(TOP_N)
other = shot_df.iloc[TOP_N:]

labels = []
sizes = []

for _, row in top.iterrows():
    labels.append(f"{row['player']} — {int(row['fgm'])}/{int(row['fga'])}")
    sizes.append(row["fga"])

if not other.empty:
    labels.append(
        f"Other — {int(other['fgm'].sum())}/{int(other['fga'].sum())}"
    )
    sizes.append(other["fga"].sum())

fig, ax = plt.subplots(figsize=(6, 6))

ax.pie(
    sizes,
    labels=labels,
    startangle=90,
    counterclock=False,
    wedgeprops={"edgecolor": "white"},
)

# ---------------- PAGE ----------------
st.title("JV Basketball – Team Dashboard")

# TEAM FIRST
st.subheader("Team Per-Game Stats")
st.dataframe(team_per_game_display)

# OPPONENT
st.subheader("Opponent Per-Game Stats")
st.dataframe(opp_pg_display)

# PLAYERS
st.subheader("Player Per-Game Averages")
st.dataframe(player_per_game_display)

# SHOT CHART
st.subheader("Shot Distribution (Season)")
st.pyplot(fig)