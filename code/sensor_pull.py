#!/usr/bin/env python3
import datetime
import sys
from turtle import pd
from sanitize import sanitize_irrimax, sanitize_groguru
from save_to_db import save_to_db
import logging
from datetime import datetime, timedelta, timezone
from get_last_pull_state import begin_sensor_pull_run, debug_peek, get_last_window_end, mark_step_done

from irrimax_scraper import main as irrimax_main
from groguru_scraper import main as groguru_main

DEFAULT_DELTA = timedelta(days=1)
OVERLAP = timedelta(hours=0.5)

logger = logging.getLogger(__name__)

def parse_iso(ts: str) -> datetime:
    """
    Parse an ISO-8601 string ending in 'Z' into a timezone-aware datetime.
    """
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)

def main():
    run_id = begin_sensor_pull_run()
    logger.info("Starting sensor pull scripts.")
    now = datetime.now(timezone.utc)

    # ── IrriMAX ──────────────────────────────────────────────────────
    start_irr = get_last_window_end(source="irrimax_save") or (now - DEFAULT_DELTA)
    if start_irr.tzinfo is None:  # normalize to UTC if old rows were naive
        start_irr = start_irr.replace(tzinfo=timezone.utc)
    start_irr = min(start_irr, now) - OVERLAP
    logger.info(f"Running IrriMAX scraper from {start_irr} to {now}...")
    try:
        irrimax_addr, irrimax_df = irrimax_main(start_irr, now)

        # mark PULL complete even if zero rows
        mark_step_done(run_id, "irrimax", "pull")
        debug_peek(run_id)  # temporary

        if irrimax_df is None or irrimax_df.empty:
            logger.info("IrriMAX returned 0 rows; skipping sanitize/save.")
            mark_step_done(run_id, "irrimax", "save")
        else:
            clean_irrimax = sanitize_irrimax(irrimax_df)
            if clean_irrimax is not None and not clean_irrimax.empty:
                save_to_db(clean_irrimax)
            mark_step_done(run_id, "irrimax", "save")

        debug_peek(run_id)  # temporary
    except Exception:
        logger.exception("IrriMAX failed")

    # ── GroGuru ─────────────────────────────────────────────────────
    start_gro = get_last_window_end(source="groguru_save") or (now - DEFAULT_DELTA)
    if start_gro.tzinfo is None:
        start_gro = start_gro.replace(tzinfo=timezone.utc)
    start_gro = min(start_gro, now) - OVERLAP
    logger.info(f"Running GroGuru scraper from {start_gro} to {now}...")
    try:
        groguru_addr, groguru_df = groguru_main(start_gro, now)
    except SystemExit as se:
        logger.warning("GroGuru main raised SystemExit (%s); treating as empty result.", se)
        groguru_addr, groguru_df = None, pd.DataFrame()

    mark_step_done(run_id, "groguru", "pull")
    debug_peek(run_id)  # temporary

    if groguru_df is None or groguru_df.empty:
        logger.info("GroGuru returned 0 rows; skipping sanitize/save.")
    else:
        clean_groguru = sanitize_groguru(groguru_df)
        if clean_groguru is not None and not clean_groguru.empty:
            save_to_db(clean_groguru)

    mark_step_done(run_id, "groguru", "save")

    debug_peek(run_id)  # temporary

    logger.debug("Sensor pull completed.")

if __name__ == "__main__":
    try:
        level = logging.INFO
        logging.basicConfig(
            level=level,
            format="%(asctime)s %(levelname)s %(message)s")
        main()
    except KeyboardInterrupt:
        logger.info("\nAborted by user.")
        sys.exit(1)
