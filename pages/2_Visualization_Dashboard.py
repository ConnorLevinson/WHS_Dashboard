import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Visualizations Dashboard", layout="wide")

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

df["reb"] = df["oreb"] + df["dreb"]
played_df = df[~df["dnp"]]

# ---------------- SHOT DISTRIBUTION ----------------
shot_df = played_df.groupby("player")[["fgm","fga"]].sum().sort_values("fga",ascending=False)
top = shot_df.head(10)
other = shot_df.iloc[10:]
labels = [f"{p} — {int(r.fgm)}/{int(r.fga)}" for p,r in top.iterrows()]
sizes = top["fga"].tolist()
if not other.empty:
    labels.append(f"Other — {int(other.fgm.sum())}/{int(other.fga.sum())}")
    sizes.append(other["fga"].sum())
fig, ax = plt.subplots(figsize=(6,6))
ax.pie(sizes, labels=labels, startangle=90, counterclock=False, wedgeprops={"edgecolor":"white"})

# ---------------- DROPDOWN ----------------
st.title("Visualization Dashboard")

viz_options = [
    "Shot Distribution (Season)"
]

selection = st.selectbox("Select Visualization", viz_options)

if selection == "Shot Distribution (Season)":
    st.subheader("Shot Distribution")
    st.pyplot(fig)
