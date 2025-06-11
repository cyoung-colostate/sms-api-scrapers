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
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
import sys
from io import StringIO
import config  # Contains IRRIMAX_API_KEY
from pathlib import Path

# Constants
BASE_URL = "https://www.irrimaxlive.com/api/"
API_KEY = config.IRRIMAX_API_KEY

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a date: {s}")

def get_loggers():
    """Fetch and parse logger details from IrriMAX Live API."""
    url = f"{BASE_URL}?cmd=getloggers&key={API_KEY}"
    response = requests.get(url)
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
                        sensor_info = {
                            "name": sensor.get("name"),
                            "depth_cm": int(sensor.get("depth_cm")),
                            "type": sensor.get("type"),
                            "unit": sensor.get("unit"),
                            "description": sensor.get("description"),
                            "min_value": float(sensor.get("minimum")),
                            "max_value": float(sensor.get("maximum"))
                        }
                        probe_info["sensors"].append(sensor_info)
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

    url = f"{BASE_URL}?{requests.compat.urlencode(params)}"
    response = requests.get(url)

    if response.status_code == 200:
        csv_data = response.text.splitlines()
        df = pd.read_csv(StringIO("\n".join(csv_data)))
        return df
    else:
        raise Exception(f"Error fetching readings: {response.status_code} - {response.text}")

def run_interactive():
    """Interactive console mode."""
    print("Choose an option:")
    print("1. List available loggers")
    print("2. Fetch readings for a specific logger")
    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        loggers = get_loggers()
        print("\nAvailable Loggers:")
        for logger in loggers:
            print(f" - {logger['name']}")
    elif choice == "2":
        logger_name = input("Enter logger name (case-sensitive): ").strip()

        while True:
            start_str = input("Enter start date (YYYY-MM-DD): ").strip()
            end_str = input("Enter end date (YYYY-MM-DD): ").strip()

            try:
                from_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                to_date = datetime.datetime.strptime(end_str, "%Y-%m-%d")

                print(f"\nFetching data for logger: {logger_name} ({from_date.date()} to {to_date.date()})...")
                df = get_readings(logger_name, from_date, to_date)

                if df.empty:
                    print("No data found for the given date range.")
                    retry = input("Try a new date range? (y/n): ").strip().lower()
                    if retry != "y":
                        print("Exiting.")
                        break
                else:
                    print(df.head())
                    break

            except ValueError as ve:
                print(f"Date Error: {ve}")
            except Exception as e:
                print(f"Error: {e}")
                break
    else:
        print("Invalid selection. Exiting.")

def run_headless(logger_name, start_str, end_str):
    """Headless execution for cloud/cron usage."""
    try:
        from_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
        to_date = datetime.datetime.strptime(end_str, "%Y-%m-%d")
        print(f"Fetching data for logger: {logger_name} ({start_str} to {end_str})...")
        df = get_readings(logger_name, from_date, to_date)

        if df.empty:
            print("No data found for the given date range.")
        else:
            print(df.head())
    except Exception as e:
        print(f"Error: {e}")
def main():
    parser = argparse.ArgumentParser(
        description="Fetch IrriMAX readings for all available loggers headless into CSV"
    )
    parser.add_argument(
        "-s", "--start", required=True, type=valid_date,
        help="Start date YYYY-MM-DD"
    )
    parser.add_argument(
        "-e", "--end", required=True, type=valid_date,
        help="End date   YYYY-MM-DD"
    )
    parser.add_argument(
        "-o", "--outfile", default=None,
        help="CSV output file name (default: irrimax_{end}.csv)"
    )

    # If no args, drop to interactive
    if len(sys.argv) == 1:
        run_interactive()
        return

    args = parser.parse_args()

    # headless: require both start and end
    if not args.start or not args.end:
        parser.error("--start and --end are required for headless mode.")

    loggers = get_loggers()
    logger_ids = [lg['logger_id'] for lg in loggers]

    dfs = []
    for lid in logger_ids:
        try:
            df = get_readings(lid, args.start, args.end)
            if not df.empty:
                df['logger_id'] = lid
                dfs.append(df)
        except Exception as e:
            print(f"Warning: {lid} failed: {e}")

    combined = pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

    if args.outfile:
        out_path = Path(args.outfile)
    else:
        out_path = Path("data") / f"irrimax_{args.end.strftime('%Y-%m-%d')}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)
    print(f"Wrote {len(combined)} records for {len(dfs)} loggers to {out_path}")

if __name__ == "__main__":
    main()
