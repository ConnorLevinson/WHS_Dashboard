import pandas as pd
from pathlib import Path

# ================== EDIT THESE FOR EACH GAME ==================
RAW_FILE = "data/raw_box_scores/260115_at_WM.csv"
GAME_ID = "2026-01-15_at_WM"
GAME_DATE = "2026-01-15"
OPPONENT = "Winters Mill"
LOCATION = "Away"   # Home / Away / Neutral
# =============================================================

# Load raw data
df = pd.read_csv(RAW_FILE)

# Clean column names
df.columns = df.columns.str.strip().str.lower()

# Ensure shooting columns are strings
for col in ["fg", "3pt", "ft"]:
    df[col] = df[col].astype(str).str.strip()

# Drop rows with no FG attempts (DNPs)
df = df[df["fg"].str.contains("-", regex=False, na=False)]

def split_made_attempted(series):
    """
    Safely split 'made-attempted' into two integer columns.
    Handles blanks, spaces, and bad formatting.
    """
    made = series.str.extract(r"(\d+)")[0]
    att = series.str.extract(r"-(\d+)")[0]

    made = pd.to_numeric(made, errors="coerce").fillna(0).astype(int)
    att = pd.to_numeric(att, errors="coerce").fillna(0).astype(int)

    return made, att

# Split shooting stats safely
df["fgm"], df["fga"] = split_made_attempted(df["fg"])
df["tpm"], df["tpa"] = split_made_attempted(df["3pt"])
df["ftm"], df["fta"] = split_made_attempted(df["ft"])

# Rename columns
df = df.rename(columns={
    "asst": "ast",
    "to": "tov"
})

# Add metadata
df["game_id"] = GAME_ID
df["date"] = GAME_DATE
df["opponent"] = OPPONENT
df["location"] = LOCATION

# Final column order
final_columns = [
    "game_id", "date", "opponent", "location", "player",
    "fgm", "fga", "tpm", "tpa", "ftm", "fta",
    "oreb", "dreb", "ast", "stl", "blk", "tov", "foul", "pts"
]

df = df[final_columns]

# Output
output_path = Path("data/player_box_scores.csv")

if output_path.exists() and output_path.stat().st_size > 0:
    df.to_csv(output_path, mode="a", header=False, index=False)
else:
    df.to_csv(output_path, index=False)

print("✅ Box score converted successfully")
