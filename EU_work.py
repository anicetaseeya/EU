# babhy
import pandas as pd
import numpy as np

FILEPATH = r"C:\Users\Nasty\Downloads\fv4m5n.xlsx"

# ----------------------------
# 1) Load Panel A from Figure 3.13 (your file structure)
# ----------------------------
raw = pd.read_excel(FILEPATH, sheet_name="Figure_3.13", header=None)

# In your sheet, Panel A lives in columns:
# col 0 = Country, col 1 = ISO3, col 2 = interconnectivity (%)
# and starts right after the row containing the word "interconnectivity".
start_idx = raw.index[raw[2].astype(str).str.contains("interconnectivity", case=False, na=False)][0] + 1

panel_a = raw.loc[start_idx:, [0, 1, 2]].copy()
panel_a.columns = ["country", "iso3", "interconnectivity_pct"]
panel_a = panel_a.dropna(subset=["country", "interconnectivity_pct"])
panel_a["interconnectivity_pct"] = pd.to_numeric(panel_a["interconnectivity_pct"], errors="coerce")
panel_a = panel_a.dropna(subset=["interconnectivity_pct"]).reset_index(drop=True)

# ----------------------------
# 2) Compute your indicators
# ----------------------------
TARGET_PCT = 15.0  # EU target ~15% (you can change to 2030 target you use)

# InterconnectionGap (in percentage points)
panel_a["interconnection_gap_pctpt"] = (TARGET_PCT - panel_a["interconnectivity_pct"]).clip(lower=0)

# "PriceBenefit ∝ InterconnectionGap" -> a normalized 0..1 score
panel_a["price_benefit_score"] = (panel_a["interconnection_gap_pctpt"] / TARGET_PCT).clip(0, 1)

# IntegrationPotential (0..1): 1 means very constrained vs target; 0 means meets/exceeds target
panel_a["integration_potential_index"] = panel_a["price_benefit_score"]

# ----------------------------
# 3) Turn it into the traffic-light labels for your tool UI
# ----------------------------
def label_status(actual_pct, target_pct=TARGET_PCT):
    if actual_pct >= target_pct:
        return "🟢 Highly interconnected"
    elif actual_pct >= 0.5 * target_pct:
        return "🟡 Moderately interconnected"
    else:
        return "🔴 Grid-constrained / high integration upside"

panel_a["status_label"] = panel_a["interconnectivity_pct"].apply(label_status)

# Optional: a user-facing sentence you can display in the app
panel_a["ui_message"] = panel_a.apply(
    lambda r: (
        f"{r['status_label']} — Interconnectivity: {r['interconnectivity_pct']:.0f}% "
        f"(gap to {TARGET_PCT:.0f}% target: {r['interconnection_gap_pctpt']:.0f} pp). "
        f"Integration upside index: {r['integration_potential_index']:.2f}."
    ),
    axis=1
)

# ----------------------------
# ----------------------------
# 4) Choose-from-list menu (console)
# ----------------------------

def print_result(r: pd.Series):
    print("\n" + r["status_label"])
    print(
        f"Interconnectivity: {r['interconnectivity_pct']:.1f}% | "
        f"Gap to {TARGET_PCT:.0f}% target: {r['interconnection_gap_pctpt']:.1f} pp | "
        f"Integration upside index: {r['integration_potential_index']:.2f}"
    )

# Build a sorted list of countries
countries = sorted(panel_a["country"].dropna().astype(str).unique().tolist())

while True:
    print("\nSelect a country (type number). Type 0 to exit.\n")

    for i, name in enumerate(countries, start=1):
        print(f"{i:>3}. {name}")

    choice = input("\nYour choice #: ").strip()

    if not choice.isdigit():
        print("Please type a number.")
        continue

    choice = int(choice)

    if choice == 0:
        break

    if not (1 <= choice <= len(countries)):
        print("Number out of range.")
        continue

    selected_country = countries[choice - 1]
    r = panel_a.loc[panel_a["country"] == selected_country].iloc[0]
    print_result(r)
