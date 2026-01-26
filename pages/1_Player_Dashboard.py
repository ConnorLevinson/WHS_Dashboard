import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Player Dashboard", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("all_games_master.csv", parse_dates=["game_date"])

df = load_data()

st.sidebar.title("Player")

player = st.sidebar.selectbox(
    "Select Player",
    sorted(df["player"].unique())
)

pdf = df[df["player"] == player].sort_values("game_date")

# ---------------- CALCULATIONS ----------------
pdf["fg_pct"] = pdf["fgm"] / pdf["fga"].replace(0, pd.NA)
pdf["3p_pct"] = pdf["3pm"] / pdf["3pa"].replace(0, pd.NA)
pdf["ft_pct"] = pdf["ftm"] / pdf["fta"].replace(0, pd.NA)
pdf["reb"] = pdf.get("oreb", 0) + pdf.get("dreb", 0)

# ---------------- HEADER ----------------
st.title(player)

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

st.altair_chart(stat_chart, use_container_width=True)

# ---------------- SHOOTING ----------------
st.subheader("Shooting Percentages")

shoot_df = pdf.melt(
    id_vars=["game_date"],
    value_vars=["fg_pct", "3p_pct", "ft_pct"],
    var_name="stat",
    value_name="pct"
)

shoot_df["stat"] = shoot_df["stat"].map({
    "fg_pct": "FG%",
    "3p_pct": "3PT%",
    "ft_pct": "FT%"
})

shoot_chart = alt.Chart(shoot_df).mark_line(point=True).encode(
    x=alt.X("game_date:T"),
    y=alt.Y("pct:Q", axis=alt.Axis(format="%")),
    color="stat:N",
    tooltip=[
        "stat",
        alt.Tooltip("pct:Q", format=".1%")
    ]
).properties(height=350)

st.altair_chart(shoot_chart, width='stretch')

# ---------------- GAME LOG ----------------
with st.expander("Game Log"):
    st.dataframe(pdf)
