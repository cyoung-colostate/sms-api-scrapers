"""
irrimax_scraper.py
Created by A.J. Brown
Agricultural Data Scientist
CSU Agricultural Water Quality Program
Ansley.Brown@colostate.edu
---------------------------
This script uses python to interact with the IrriMAX Live API v1.9 to retrieve soil 
sensor data.

URL: https://www.irrimaxlive.com/help/api.html
Example Call: https://www.irrimaxlive.com/api/?cmd=getreadings&name=Soybeans%201&from=20110911000000&key=APIKEYHERE


TODO:
- Merge data from single sensor with metadata into TBD format for WISE Pro input.
- Test code for functionality.
"""

import requests
import xml.etree.ElementTree as ET
import pandas as pd
import datetime
import config  # Import API key from config.py

# Constants
BASE_URL = "https://www.irrimaxlive.com/api/"
API_KEY = config.API_KEY

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
        df = pd.read_csv(pd.compat.StringIO("\n".join(csv_data)))
        return df
    else:
        raise Exception(f"Error fetching readings: {response.status_code} - {response.text}")

if __name__ == "__main__":
    try:
        loggers = get_loggers()
        print(f"Available Loggers: {[logger['name'] for logger in loggers]}")
        
        # Fetch data for the first logger
        if loggers:
            selected_logger = loggers[0]["name"]
            print(f"Fetching data for logger: {selected_logger}")

            # Define time range (last 7 days)
            to_date = datetime.datetime.utcnow()
            from_date = to_date - datetime.timedelta(days=7)

            df = get_readings(selected_logger, from_date, to_date)
            print(df.head())  # Display the first few rows

    except Exception as e:
        print(f"Error: {e}")
