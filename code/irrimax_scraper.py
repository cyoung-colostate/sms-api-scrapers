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
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
import sys
from io import StringIO
import config  # Contains IRRIMAX_API_KEY
from pathlib import Path
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed, Future

logger = logging.getLogger(__name__)

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    level=logging.INFO
)

session = requests.Session()

# Constants
BASE_URL = "https://www.irrimaxlive.com/api/"
API_KEY = config.IRRIMAX_API_KEY

def parse_datetime(s: str, default_to_end: bool) -> datetime.datetime:
    """
    Parse either a YYYY-MM-DD or a full ISO‐style YYYY-MM-DDTHH:MM:SS.
    If only a date is given, set time = 00:00:00 (default_to_end=False)
    or = 23:59:59 (default_to_end=True).
    """
    # try full timestamp first
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.datetime.strptime(s, fmt)
        except ValueError:
            pass

    # fall back to date only
    try:
        dt = datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a valid date or datetime: {s!r}")
    
    if default_to_end:
        return dt.replace(hour=23, minute=59, second=59)
    else:
        return dt.replace(hour=0, minute=0, second=0)

def valid_start(s: str) -> datetime.datetime:
    return parse_datetime(s, default_to_end=False)

def valid_end(s: str) -> datetime.datetime:
    return parse_datetime(s, default_to_end=True)


def parse_sensor(sensor_elem: ET.Element) -> dict:
    """
    Parse an XML <Sensor> element into a dict with the same keys
    you were assembling in get_loggers().
    """
    return {
        "name":        sensor_elem.get("name"),
        "depth_cm":    int(sensor_elem.get("depth_cm", -1)),
        "type":        sensor_elem.get("type"),
        "unit":        sensor_elem.get("unit"),
        "description": sensor_elem.get("description"),
        "min_value":   float(sensor_elem.get("minimum", -1)),
        "max_value":   float(sensor_elem.get("maximum", -1)),
    }

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

def get_loggers():
    """Fetch and parse logger details from IrriMAX Live API."""
    url = f"{BASE_URL}?cmd=getloggers&key={API_KEY}"
    response = session.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        loggers = []
        for logger in root.findall("Logger"):
            logger_info = {
                "id": logger.get("id"),
                "name": logger.get("name"),
                "logger_id": logger.get("logger_id"),
                "latitude": float(logger.get("latitude")),
                "longitude": float(logger.get("longitude")),
                "sites": []
            }
            for site in logger.findall("Site"):
                site_info = {
                    "name": site.get("name"),
                    "probes": []
                }
                for probe in site.findall("Probe"):
                    probe_info = {
                        "name": probe.get("name"),
                        "sensors": []
                    }
                    for sensor in probe.findall("Sensor"):
                        probe_info["sensors"].append(parse_sensor(sensor))
                    site_info["probes"].append(probe_info)
                logger_info["sites"].append(site_info)
            loggers.append(logger_info)
        return loggers
    else:
        raise Exception(f"Error fetching loggers: {response.status_code} - {response.text}")

def get_readings(logger_name, from_date=None, to_date=None):
    """Retrieve soil moisture sensor readings for a specific logger and return as a pandas DataFrame."""
    if from_date and to_date and from_date > to_date:
        raise ValueError("Start date must be before end date.")

    params = {
        "cmd": "getreadings",
        "key": API_KEY,
        "name": logger_name,
    }
    if from_date:
        params["from"] = from_date.strftime("%Y%m%d%H%M%S")
    if to_date:
        params["to"] = to_date.strftime("%Y%m%d%H%M%S")

    response = session.get(
        BASE_URL,
        params=params,
        timeout=10
    )
    response.raise_for_status()

    csv_data = response.text.splitlines()
    df = pd.read_csv(StringIO("\n".join(csv_data)))
    return df
   
def run_interactive():
    """Interactive console mode."""
    logger.info("Choose an option:")
    logger.info("1. List available loggers")
    logger.info("2. Fetch readings for a specific logger")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        loggers = get_loggers()
        logger.info("\nAvailable Loggers:")
        for logger in loggers:
            logger.info(f" - {logger['name']}")
    elif choice == "2":
        logger_name = input("Enter logger name (case-sensitive): ").strip()

        while True:
            start_str = input("Enter start date or datetime (YYYY-MM-DD[THH:MM:SS]): ").strip()
            end_str   = input("Enter end   date or datetime (YYYY-MM-DD[THH:MM:SS]): ").strip()

            try:
                from_date = valid_start(start_str)
                to_date   = valid_end(end_str)
                logger.info(f"\nFetching data for logger: {logger_name} ({from_date.date()} to {to_date.date()})...")
                df = get_readings(logger_name, from_date, to_date)

                if df.empty:
                    logger.info("No data found for the given date range.")
                    retry = input("Try a new date range? (y/n): ").strip().lower()
                    if retry != "y":
                        logger.info("Exiting.")
                        break
                else:
                    logger.info(df.head())
                    break

            except argparse.ArgumentTypeError as e:
                    logger.error("Bad date/time: %s", e)
                    continue
            except ValueError as ve:
                logger.error(f"Date Error: {ve}")
            except Exception as e:
                logger.error(f"Error: {e}")
                break
    else:
        logger.error("Invalid selection. Exiting.")

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
    # no args → interactive mode
    if len(sys.argv) == 1:
        run_interactive()
        sys.exit(0)
    
    args = parse_args()
    main(args.start, args.end, args.outfile)