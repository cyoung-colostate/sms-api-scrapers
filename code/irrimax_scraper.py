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

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
import sys
from io import StringIO
import config  # Contains IRRIMAX_API_KEY

# Constants
BASE_URL = "https://www.irrimaxlive.com/api/"
API_KEY = config.IRRIMAX_API_KEY

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

if __name__ == "__main__":
    if len(sys.argv) == 4:
        # Headless (cron/server) mode
        _, logger_arg, start_arg, end_arg = sys.argv
        run_headless(logger_arg, start_arg, end_arg)
    else:
        # Interactive mode
        run_interactive()


# '''
# Example Run:

# Interactive mode:
# (playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python irrimax_scraper.py
# Choose an option:
# 1. List available loggers
# 2. Fetch readings for a specific logger
# Enter 1 or 2: 2
# Enter logger name (case-sensitive): 8A_8
# Enter start date (YYYY-MM-DD): 2024-06-10
# Enter end date (YYYY-MM-DD): 2024-10-15

# Fetching data for logger: 8A_8 (2024-06-10 to 2024-10-15)...
#              Date Time      V1      V2     A1(5)     S1(5)  ...    S8(75)    T8(75)    A9(85)    S9(85)  T9(85)
# 0  2024/06/10 00:00:00  13.735  13.474  16.63106  379.6608  ...  844.3812  17.04999  40.48423  4438.727   16.72
# 1  2024/06/10 00:30:00  13.769  -1.000  16.62494  376.4792  ...  844.4537  17.04999  40.48423  4438.727   16.72
# 2  2024/06/10 01:00:00  13.787  -1.000  16.62494  378.4209  ...  844.3812  17.01999  40.49162  4439.438   16.72
# 3  2024/06/10 01:30:00  13.783  -1.000  16.58220  373.6646  ...  844.0801  16.95001  40.46944  4437.237   16.75
# 4  2024/06/10 02:00:00  13.707  -1.000  16.60052  373.4932  ...  844.3039  17.00000  40.49162  4422.122   16.72

# [5 rows x 30 columns]


# Headless mode:
# (playground2) C:\Users\ansle\OneDrive\Documents\GitHub\sms-api-scrapers\code>python irrimax_scraper.py 8A_8 2024-06-10 2024-10-15
# Fetching data for logger: 8A_8 (2024-06-10 to 2024-10-15)...
#              Date Time      V1      V2     A1(5)     S1(5)  ...    S8(75)    T8(75)    A9(85)    S9(85)  T9(85)
# 0  2024/06/10 00:00:00  13.735  13.474  16.63106  379.6608  ...  844.3812  17.04999  40.48423  4438.727   16.72
# 1  2024/06/10 00:30:00  13.769  -1.000  16.62494  376.4792  ...  844.4537  17.04999  40.48423  4438.727   16.72
# 2  2024/06/10 01:00:00  13.787  -1.000  16.62494  378.4209  ...  844.3812  17.01999  40.49162  4439.438   16.72
# 3  2024/06/10 01:30:00  13.783  -1.000  16.58220  373.6646  ...  844.0801  16.95001  40.46944  4437.237   16.75
# 4  2024/06/10 02:00:00  13.707  -1.000  16.60052  373.4932  ...  844.3039  17.00000  40.49162  4422.122   16.72

# [5 rows x 30 columns]

# '''