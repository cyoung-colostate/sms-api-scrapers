import requests
import xml.etree.ElementTree as ET
import pandas as pd
from io import StringIO
import config  # Contains IRRIMAX_API_KEY
import logging
import hashlib
import os

logger = logging.getLogger(__name__)

try:
    logger.info("Config file: %s", getattr(config, "__file__", "<no __file__>"))
    key_repr = getattr(config, "IRRIMAX_API_KEY", None)
    if key_repr:
        logger.info("IRRIMAX_API_KEY fingerprint: sha1=%s", hashlib.sha1(key_repr.encode()).hexdigest()[:10])
    else:
        logger.error("IRRIMAX_API_KEY is missing!")
except Exception as _e:
    logger.error("Config inspection failed: %r", _e)

session = requests.Session()

# Constants
BASE_URL = "https://www.irrimaxlive.com/api/"
API_KEY = os.getenv("IRRIMAX_API_KEY", getattr(config, "IRRIMAX_API_KEY", None))

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

def get_loggers():
    """Fetch and parse logger details from IrriMAX Live API."""
    url = f"{BASE_URL}?cmd=getloggers&key={API_KEY}"
    response = session.get(
        url, 
        headers={"Cache-Control": "no-cache"},
        timeout=60
    )
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
        headers={"Cache-Control": "no-cache"},
        params=params,
        timeout=20
    )
    response.raise_for_status()

    csv_data = response.text.splitlines()
    df = pd.read_csv(StringIO("\n".join(csv_data)))
    return df