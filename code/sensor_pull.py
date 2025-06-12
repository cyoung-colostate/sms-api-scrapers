#!/usr/bin/env python3
import json
import datetime
import sys
from pathlib import Path
from sanitize import sanitize_irrimax, sanitize_groguru
from save_to_db import save_to_db
import logging

from irrimax_scraper import main as irrimax_main
from groguru_scraper import main as groguru_main

STATE_FILE = Path("last_pull_state.json")
DEFAULT_DELTA = datetime.timedelta(days=1)

logger = logging.getLogger("__name__")

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
    logger.info("Starting sensor pull scripts...")
    now = datetime.datetime.now(datetime.timezone.utc)
    now_iso = now.isoformat().replace("+00:00", "Z")

    state = load_state()

    # ── IrriMAX ──────────────────────────────────────────────────────
    last_irr = state.get("irrimax")
    if last_irr:
        start_irr = parse_iso(last_irr)
    else:
        start_irr = now - DEFAULT_DELTA

    logger.info(f"Running IrriMAX scraper from {start_irr} to {now}...")
    try:
        irrimax_address, irrimax_df = irrimax_main(start_irr, now)
        state["irrimax"] = now_iso
    except Exception as e:
        logger.error("  ✗ IrriMAX scraper failed:", e)

    # ── GroGuru ─────────────────────────────────────────────────────
    last_gro = state.get("groguru")
    if last_gro:
        start_gro = parse_iso(last_gro)
    else:
        start_gro = now - DEFAULT_DELTA

    logger.info(f"Running GroGuru scraper from {start_gro} to {now}...")
    try:
        gorguru_address, groguru_df = groguru_main(start_gro, now)
        state["groguru"] = now_iso
    except Exception as e:
        logger.error("  ✗ GroGuru scraper failed:", e)

    # persist any updated timestamps
    save_state(state)
    logger.debug("Sensor pull completed.")

    logger.debug("IrriMAX data:", irrimax_address)
    logger.debug("GroGuru data:", gorguru_address)

    clean_irrimax = sanitize_irrimax(irrimax_df)
    clean_groguru = sanitize_groguru(groguru_df)

    try:
        save_to_db(clean_irrimax)
        logger.info("IrriMAX data saved to database.")
    except Exception as e:
        logger.error("  ✗ Failed to save IrriMAX data to database:", e)

    try:
        save_to_db(clean_groguru)
        logger.info("GroGuru data saved to database.")
    except Exception as e:
        logger.error("  ✗ Failed to save GroGuru data to database:", e)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nAborted by user.")
        sys.exit(1)
