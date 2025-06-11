#!/usr/bin/env python3
import json
import datetime
import sys
from pathlib import Path

from irrimax_scraper import main as irrimax_main
from groguru_scraper import main as groguru_main
import re
import pandas as pd

STATE_FILE = Path("last_pull_state.json")
DEFAULT_DELTA = datetime.timedelta(days=1)

def parse_iso(ts: str) -> datetime.datetime:
    """
    Parse an ISO-8601 string ending in 'Z' into a timezone-aware datetime.
    """
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.datetime.fromisoformat(ts)

def load_state() -> dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def main():
    print("Starting sensor pull scripts...")
    now = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now.isoformat().replace("+00:00", "Z")

    state = load_state()

    # ── IrriMAX ──────────────────────────────────────────────────────
    last_irr = state.get("irrimax")
    if last_irr:
        start_irr = parse_iso(last_irr)
    else:
        start_irr = now - DEFAULT_DELTA

    print(f"Running IrriMAX scraper from {start_irr} to {now}...")
    try:
        irrimax_address, irrimax_df = irrimax_main(start_irr, now)
        state["irrimax"] = now_iso
    except Exception as e:
        print("  ✗ IrriMAX scraper failed:", e)

    # ── GroGuru ─────────────────────────────────────────────────────
    last_gro = state.get("groguru")
    if last_gro:
        start_gro = parse_iso(last_gro)
    else:
        start_gro = now - DEFAULT_DELTA

    print(f"Running GroGuru scraper from {start_gro} to {now}...")
    try:
        gorguru_address, groguru_df = groguru_main(start_gro, now)
        state["groguru"] = now_iso
    except Exception as e:
        print("  ✗ GroGuru scraper failed:", e)


    # persist any updated timestamps
    save_state(state)
    print("Sensor pull completed.")

    print("IrriMAX data:", irrimax_address)
    print ("GroGuru data:", gorguru_address)
    print(groguru_df.head())

    sanitize_irrimax(irrimax_df)
    sanitize_groguru(groguru_df)



def sanitize_groguru(groguru_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert the raw GroGuru DataFrame into a sanitized format suitable for Postgres.
    Columns produced:
      - source: 'groguru'
      - logger_id: None (or you can modify to use site/device if available)
      - timestamp: original timestamp column
      - depth: list of sensor indices (integers)
      - vwc: list of values from moistureX columns, in index order
      - conductivity: list of values from conductivityX columns, in index order
      - temperature: list of values from temp_fX columns, in index order
      - available_water: list of values from awX columns, in index order
    """
    # Patterns for each metric
    moisture_pattern = re.compile(r"^moisture(\d+)$", re.IGNORECASE)
    cond_pattern     = re.compile(r"^conductivity(\d+)$", re.IGNORECASE)
    temp_pattern     = re.compile(r"^temp_f(\d+)$", re.IGNORECASE)
    aw_pattern       = re.compile(r"^aw(\d+)$", re.IGNORECASE)

    moisture_info = []
    cond_info     = []
    temp_info     = []
    aw_info       = []

    for col in groguru_df.columns:
        m = moisture_pattern.match(col)
        if m:
            idx = int(m.group(1))
            moisture_info.append((idx, col))
            continue
        m = cond_pattern.match(col)
        if m:
            idx = int(m.group(1))
            cond_info.append((idx, col))
            continue
        m = temp_pattern.match(col)
        if m:
            idx = int(m.group(1))
            temp_info.append((idx, col))
            continue
        m = aw_pattern.match(col)
        if m:
            idx = int(m.group(1))
            aw_info.append((idx, col))

    # Sort each metric by the sensor index
    moisture_info.sort(key=lambda x: x[0])
    cond_info.sort(key=lambda x: x[0])
    temp_info.sort(key=lambda x: x[0])
    aw_info.sort(key=lambda x: x[0])

    # Extract lists of column names and indices
    depths = [idx for idx, _ in temp_info]  # use temp indices as depths
    vwc_cols       = [col for _, col in moisture_info]
    cond_cols      = [col for _, col in cond_info]
    temp_cols      = [col for _, col in temp_info]
    aw_cols        = [col for _, col in aw_info]

    # Build the clean DataFrame
    clean_df = pd.DataFrame({
        "source":         "groguru",
        "logger_id":      None,
        "timestamp":      pd.to_datetime(groguru_df["timestamp"]),
        "depth":          [depths] * len(groguru_df),
        "vwc":            groguru_df[vwc_cols].values.tolist(),
        "conductivity":   groguru_df[cond_cols].values.tolist(),
        "temperature":    groguru_df[temp_cols].values.tolist(),
        "available_water":groguru_df[aw_cols].values.tolist(),
    })

    # Display for verification
    print(clean_df.head().to_string(index=False))
    return clean_df


def sanitize_irrimax(irrimax_df):
    # 1) Extract (index, depth, col) for A, S, T columns
    a_pattern = re.compile(r"^A(\d+)\((\d+)\)$")
    s_pattern = re.compile(r"^S(\d+)\((\d+)\)$")
    t_pattern = re.compile(r"^T(\d+)\((\d+)\)$")

    a_info = []
    s_info = []
    t_info = []

    for col in irrimax_df.columns:
        m = a_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            a_info.append((idx, depth, col))
        m = s_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            s_info.append((idx, depth, col))
        m = t_pattern.match(col)
        if m:
            idx, depth = int(m.group(1)), int(m.group(2))
            t_info.append((idx, depth, col))

    # 2) Sort by the numeric index
    a_info.sort(key=lambda x: x[0])
    s_info.sort(key=lambda x: x[0])
    t_info.sort(key=lambda x: x[0])

    # 3) Build lists of depths and column names
    depths = [depth for _, depth, _ in a_info]
    vwc_cols = [col for _, _, col in a_info]
    cond_cols = [col for _, _, col in s_info]
    temp_cols = [col for _, _, col in t_info]

    # 4) Construct the new DataFrame
    clean_df = pd.DataFrame({
        "source": "irrimax",
        "logger_id": irrimax_df["logger_id"],
        "timestamp": pd.to_datetime(irrimax_df["Date Time"], format="%Y/%m/%d %H:%M:%S"),
        "depth": [depths] * len(irrimax_df),
        "vwc": irrimax_df[vwc_cols].values.tolist(),
        "conductivity": irrimax_df[cond_cols].values.tolist(),
        "temperature": irrimax_df[temp_cols].values.tolist(),
    })

    # Display the cleaned DataFrame
    print(clean_df.head().to_string(index=False))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.")
        sys.exit(1)
