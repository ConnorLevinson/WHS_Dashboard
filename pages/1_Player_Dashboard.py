import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Player Dashboard", layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("all_games_master.csv", parse_dates=["game_date"])

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("Player")

player = st.sidebar.selectbox(
    "Select Player",
    sorted(df["player"].unique())
)

pdf = df[df["player"] == player].sort_values("game_date")

# ---------------- CALCULATIONS ----------------

# Convert shooting columns to numeric safely
for col in ["fgm", "fga", "3pm", "3pa", "ftm", "fta"]:
    pdf[col] = pd.to_numeric(pdf[col], errors="coerce")

# Replace 0 attempts with NaN to avoid division by zero
pdf["fga"].replace(0, np.nan, inplace=True)
pdf["3pa"].replace(0, np.nan, inplace=True)
pdf["fta"].replace(0, np.nan, inplace=True)

# Compute percentages, multiply by 100, round to 1 decimal
pdf["fg_pct"] = ((pdf["fgm"] / pdf["fga"]) * 100).round(1)
pdf["3p_pct"] = ((pdf["3pm"] / pdf["3pa"]) * 100).round(1)
pdf["ft_pct"] = ((pdf["ftm"] / pdf["fta"]) * 100).round(1)

# Total rebounds
pdf["reb"] = pdf.get("oreb", 0) + pdf.get("dreb", 0)

# ---------------- HEADER ----------------
st.title(player)

# ---------------- GAME LOG ----------------
clean_pdf = pdf.drop(columns=['foul', 'game_date', 'location'])

# Format percentages for display with % sign
for col in ["fg_pct", "3p_pct", "ft_pct"]:
    clean_pdf[col] = clean_pdf[col].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")

st.subheader("Game Log")
columns = ["opponent", "pts", "reb", "asst", "to","stl", "blk", "fg_pct","3p_pct","ft_pct","fgm","fga","3pm","3pa","ftm","fta","oreb","dreb","dnp"]
st.dataframe(clean_pdf[columns])

# ---------------- PER GAME STATS ----------------
st.subheader("Per Game Stats")

long_df = pdf.melt(
    id_vars=["game_date"],
    value_vars=["pts", "reb", "asst", "stl", "blk", "to"],
    var_name="stat",
    value_name="value"
)

stat_chart = alt.Chart(long_df).mark_line(point=True).encode(
    x=alt.X("game_date:T", title="Game"),
    y=alt.Y("value:Q", title="Value"),
    color=alt.Color("stat:N", title="Stat"),
    tooltip=["stat", "value"]
).properties(height=350)

st.altair_chart(stat_chart, width='stretch')
