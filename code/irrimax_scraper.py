"""
irrimax_scraper.py
Created by A.J. Brown
Agricultural Data Scientist
CSU Agricultural Water Quality Program
Ansley.Brown@colostate.edu
---------------------------
This script uses Python to interact with the IrriMAX Live API v1.9 to retrieve soil 
sensor data for use in WISE Pro. Supports both interactive and headless (server) use.

URL: https://www.irrimaxlive.com/help/api.html
Example Call: https://www.irrimaxlive.com/api/?cmd=getreadings&name=Soybeans%201&from=20110911000000&key=APIKEYHERE


Data units:
Sensor columns are structured as `<Type><Index>(<Depth>)`, for example, `A3(25)` means the third moisture sensor at 25 cm depth.

| Prefix | Sensor Type                              | Units            | Notes                                 |
|--------|------------------------------------------|------------------|---------------------------------------|
| `A`    | Soil Moisture (Volumetric Water Content) | %                | Based on depth (e.g., `A1(5)`)        |
| `S`    | Soil Salinity (Electrical Conductivity)  | µS/cm            | Based on depth (e.g., `S1(5)`)        |
| `T`    | Soil Temperature                         | °C               | Based on depth (e.g., `T1(5)`)        |
| `V`    | Voltage                                  | Volts (V)        | System voltages, not tied to depth    |

"""
import argparse
from typing import Tuple, Optional
import pandas as pd
import datetime
from irrimax_methods import get_readings, get_loggers
from datetime_helpers import valid_start, valid_end
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

logger = logging.getLogger(__name__)

def fetch_for_logger(lid: str, start: datetime.datetime, end: datetime.datetime):
    """
    Wrapper around get_readings() that catches and logs errors,
    and returns a DataFrame (or None on failure/empty).
    """
    try:
        df = get_readings(lid, start, end)
        if not df.empty:
            df["logger_id"] = lid
            return df
    except Exception as e:
        logger.warning("Logger %s failed: %s", lid, e)
    return None
   
def parse_args():
    parser = argparse.ArgumentParser(
        description="Fetch IrriMAX readings for all available loggers headless into CSV"
    )
    parser.add_argument(
        "-s", "--start",
        required=True,
        type=valid_start,
        help="Start date or datetime.  YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
    )
    parser.add_argument(
        "-e", "--end",
        required=True,
        type=valid_end,
        help="End date or datetime.  YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
    )
    parser.add_argument(
        "-o", "--outfile",
        default=None,
        help="CSV file (default: data/irrimax_{end}.csv)"
    )
    args = parser.parse_args()
    return args

def main(start: datetime.datetime,
         end:   datetime.datetime,
         outfile: str | None = None
) -> Tuple[Path, pd.DataFrame]:
    loggers    = get_loggers()
    logger_ids = [lg["logger_id"] for lg in loggers]

    # 1) fire off all fetches in parallel, remembering each index
    futures: dict[Future, int] = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        for idx, lid in enumerate(logger_ids):
            fut = executor.submit(fetch_for_logger, lid, start, end)
            futures[fut] = idx

        # 2) collect into a pre-sized list so order matches logger_ids
        results: list[Optional[pd.DataFrame]] = [None] * len(logger_ids)
        for fut in as_completed(futures):
            idx = futures[fut]
            results[idx] = fut.result()

    # 3) drop any Nones and concatenate in original order
    dfs = [df for df in results if df is not None]
    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    # 4) write the CSV (filename based on timestamp or --outfile)
    if outfile:
        out_path = Path(outfile)
    else:
        start_timestamp = start.strftime("%Y%m%d%H%M%S")
        end_timestamp = end.strftime("%Y%m%d%H%M%S")
        out_path = Path("data") / f"irrimax_{start_timestamp}_{end_timestamp}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)

    logger.info(f"Wrote {len(combined)} records for {len(dfs)} loggers to {out_path}")
    return out_path, combined

if __name__ == "__main__":
    args = parse_args()
    main(args.start, args.end, args.outfile)