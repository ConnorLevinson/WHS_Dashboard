import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/opponent_team_stats.csv")

# -----------------------------------
# Helper function
# -----------------------------------
def get_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a valid number.")

# -----------------------------------
# Collect Opponent Info
# -----------------------------------
print("\n🏀 Enter Opponent Team Stats\n")

# ================== EDIT THESE FOR EACH GAME ==================
GAME_ID = "2025-12-05_at_TJ"
GAME_DATE = "2025-12-05"
OPPONENT = "Governor Thomas Johnson"
LOCATION = "Away"   # Home / Away / Neutral
# =============================================================

print("\n--- Shooting ---")
fgm = get_int("FG Made: ")
fga = get_int("FG Attempts: ")
tpm = get_int("3PT Made: ")
tpa = get_int("3PT Attempts: ")
ftm = get_int("FT Made: ")
fta = get_int("FT Attempts: ")

print("\n--- Other Stats ---")
pts = get_int("Points: ")
oreb = get_int("Offensive Rebounds: ")
dreb = get_int("Defensive Rebounds: ")
tov = get_int("Turnovers: ")

# -----------------------------------
# Build Row
# -----------------------------------
row = {
    "game_id": GAME_ID,
    "date": GAME_DATE,
    "opponent": OPPONENT,
    "location": LOCATION,
    "pts": pts,
    "fgm": fgm,
    "fga": fga,
    "tpm": tpm,
    "tpa": tpa,
    "ftm": ftm,
    "fta": fta,
    "oreb": oreb,
    "dreb": dreb,
    "tov": tov
}

df_new = pd.DataFrame([row])

# -----------------------------------
# Append or Create File
# -----------------------------------
if DATA_PATH.exists():
    df_existing = pd.read_csv(DATA_PATH)
    df_final = pd.concat([df_existing, df_new], ignore_index=True)
else:
    df_final = df_new

df_final.to_csv(DATA_PATH, index=False)

print("\n✅ Opponent stats saved successfully!")
