import pandas as pd
import glob
import os
from datetime import datetime

# -------- CONFIG --------
DATA_FOLDER = "data/raw_box_scores"   # folder with your stat files
OUTPUT_FILE = "all_games_master.csv"

# -------- HELPERS --------
def parse_filename(filename):
    """
    251205_at_GovThomasJohnson.csv
    """
    name = os.path.basename(filename).replace(".csv", "")
    parts = name.split("_")

    date = datetime.strptime(parts[0], "%y%m%d").date()

    loc_map = {
        "vs": "home",
        "at": "away",
        "neutral": "neutral"
    }
    location = loc_map.get(parts[1], "unknown")

    opponent = " ".join(parts[2:])

    return date, location, opponent


def split_made_attempt(val):
    """
    '3-9' -> (3, 9)
    '-'   -> (0, 0)
    """
    if val.strip() == "-":
        return 0, 0
    made, att = val.split("-")
    return int(made), int(att)


# -------- MAIN --------
all_games = []

for file in glob.glob(os.path.join(DATA_FOLDER, "*.csv")):
    df = pd.read_csv(file)

    # clean column names
    df.columns = [c.strip() for c in df.columns]

    game_date, location, opponent = parse_filename(file)

    # DNP flag
    df["dnp"] = df["fg"].astype(str).str.strip() == "-"

    # split shooting stats
    df[["fgm", "fga"]] = df["fg"].apply(lambda x: pd.Series(split_made_attempt(str(x))))
    df[["3pm", "3pa"]] = df["3pt"].apply(lambda x: pd.Series(split_made_attempt(str(x))))
    df[["ftm", "fta"]] = df["ft"].apply(lambda x: pd.Series(split_made_attempt(str(x))))

    # numeric columns (everything else)
    numeric_cols = ["oreb", "dreb", "foul", "stl", "to", "blk", "asst", "pts"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # metadata
    df["game_date"] = game_date
    df["location"] = location
    df["opponent"] = opponent

    # drop original shooting columns
    df = df.drop(columns=["fg", "3pt", "ft"])

    all_games.append(df)

# combine everything
master_df = pd.concat(all_games, ignore_index=True)

# save
master_df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved {len(master_df)} rows to {OUTPUT_FILE}")

