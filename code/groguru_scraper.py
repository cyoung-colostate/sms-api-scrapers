'''
groguru_scraper.py
Created by A.J. Brown
Agricultural Data Scientist
CSU Agricultural Water Quality Program
Ansley.Brown@colostate.edu
---------------------------
This script interacts with the GroGuru InSites API to retrieve soil moisture sensor data.

Reference: https://groguruinsites.docs.apiary.io/
'''

from pathlib import Path
import requests
import datetime
import pandas as pd
import sys
import argparse
import config  # Contains GROGURU_EMAIL and GROGURU_PASSWORD
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

# === CONFIGURABLE CREDENTIALS ===
GROGURU_USERNAME = config.GROGURU_USERNAME
GROGURU_PASSWORD = config.GROGURU_PASSWORD

# === CONSTANTS ===
BASE_URL = "https://api.groguru.com"
LOGIN_ENDPOINT = f"{BASE_URL}/user/signin"
ORG_VIEW_ENDPOINT = f"{BASE_URL}/org/view/{{user_id}}"
# GRAPH_DATA_ENDPOINT = f"{BASE_URL}/stem/graph-data/{{siteId}}/{{deviceId}}/"

def make_session():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session

SESSION = make_session()

def valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Not a date: {s}")
    
def authenticate(email, password):
    """Authenticate with the GroGuru API and return a token and user ID."""
    logger.info("Authenticating with GroGuru API...")
    payload = {"email": email, "password": password}
    response = SESSION.post(LOGIN_ENDPOINT, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info(f"Login successful. User: {data['data']['username']}")
            return data['data']['sessionToken'], data['data']['id']
        else:
            logger.info("Login failed. Message:", data.get("message", "No message returned."))
            sys.exit(1)
    else:
        logger.info(f"Login failed. HTTP {response.status_code} - {response.text}")
        sys.exit(1)

def get_organization_view(token, userid):
    """Retrieve the organization view data for the authenticated user."""
    logger.debug("Fetching organization view...")
    headers = {"Authorization": token}
    response = SESSION.get(ORG_VIEW_ENDPOINT.format(user_id=userid), headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            logger.info("Successfully fetched organization data.")
            return data["data"]
        else:
            logger.info("Failed to retrieve organization data:", data.get("message", "No message."))
    else:
        logger.info(f"Failed to get organization view. HTTP {response.status_code} - {response.text}")
    return None

def list_sites_from_org(org_data):
    """Flatten and extract site and device information from organization data."""
    logger.info("Extracting sites and devices from organization data...")
    site_dict = {}
    try:
        for farm in org_data.get("children", []):
            for site in farm.get("sites", []):
                site_id = site.get("siteId")
                if site_id not in site_dict:
                    site_dict[site_id] = {
                        "farm": farm.get("name"),
                        "name": site.get("name"),
                        "siteId": site_id,
                        "devices": []
                    }
                site_dict[site_id]["devices"].append(site.get("twigId"))
    except KeyError:
        logger.info("Unexpected format in org view response.")
    return list(site_dict.values())

def flatten_graph_data(graph):
    """Flatten the nested graph JSON data into a flat DataFrame."""
    all_data = {}
    for key, content in graph.items():
        abs_data = content.get("absolute")
        if not abs_data:
            continue
        for entry in abs_data:
            ts = entry.get("xValue")
            if not ts:
                continue
            if ts not in all_data:
                all_data[ts] = {}
            for k, v in entry.items():
                if k != "xValue":
                    col_name = f"{key}{k}" if k.isdigit() else key
                    all_data[ts][col_name] = v
    df = pd.DataFrame.from_dict(all_data, orient="index")
    df.index.name = "timestamp"
    df.reset_index(inplace=True)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def get_raw_json(token, site_id, device_id, from_date, to_date):
    """Fetch raw JSON data from the GroGuru API for a given site and device."""
    headers = {"Authorization": token}
    params = {
        "fromDate": from_date.strftime("%Y-%m-%d"),
        "toDate": to_date.strftime("%Y-%m-%d"),
        "limit": 1000
    }
    url = f"{BASE_URL}/stem/graph-data/{site_id}/{device_id}/"
    response = SESSION.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching raw JSON: HTTP {response.status_code} - {response.text}")

def get_readings(token, site_id, device_id, from_date, to_date):
    """Fetch flattened sensor readings DataFrame for a site/device/date range."""
    logger.debug(f"Fetching readings for site {site_id} and device {device_id} from {from_date.date()} to {to_date.date()}...")
    json_data = get_raw_json(token, site_id, device_id, from_date, to_date)
    graph_data = json_data.get("data", {}).get("graph", {})
    if not graph_data:
        logger.debug("No graph data returned.")
        return pd.DataFrame()
    df_flat = flatten_graph_data(graph_data)
    return df_flat

def get_brute_force_readings(token, site_id, device_id, from_date, to_date, step_hours=2):
    """Repeatedly call `get_readings` over 2-hour intervals to overcome data limits."""
    logger.info(f"Brute force fetching from {from_date} to {to_date} in {step_hours}-hour chunks...")
    delta = datetime.timedelta(hours=step_hours)
    current_start = from_date
    all_chunks = []

    while current_start < to_date:
        current_end = min(current_start + delta, to_date)
        try:
            chunk_df = get_readings(token, site_id, device_id, current_start, current_end)
            if not chunk_df.empty:
                all_chunks.append(chunk_df)
        except Exception as e:
            logger.info(f"Warning: Failed to fetch from {current_start} to {current_end}: {e}")
        current_start = current_end

    if not all_chunks:
        logger.info("No data retrieved.")
        return pd.DataFrame()

    merged_df = (
        pd.concat(all_chunks)
        .drop_duplicates(subset="timestamp")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    logger.info(f"Retrieved {len(merged_df)} rows total.")
    return merged_df

def fetch_one(params):
    token, site, device, from_date, to_date, brute_force, step_hours = params
    try:
        df = (get_brute_force_readings if brute_force else get_readings)(
            token, site["siteId"], device, from_date, to_date, step_hours
        )
        df["farm"], df["site"], df["device"] = site["farm"], site["name"], device
        return site["siteId"], device, df, None
    except Exception as e:
        return site["siteId"], device, None, str(e)

def collect_readings_parallel(token, sites, from_date, to_date, brute_force=False, step_hours=2):
    tasks = []
    for site in sites:
        for device in site["devices"]:
            tasks.append((token, site, device, from_date, to_date, brute_force, step_hours))

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_one, t): t for t in tasks}
        for fut in as_completed(futures):
            sid, dev, df, err = fut.result()
            if err:
                logger.warning(f"{sid}/{dev} failed: {err}")
            elif not df.empty:
                results.append(df)
    return results

def collect_readings(token, sites, from_date, to_date, brute_force=False, step_hours=2):
    all_dfs = []  # <-- collect here

    for site in sites:
        site_id   = site["siteId"]
        site_name = site["name"]
        for device_id in site["devices"]:
            logger.info(f"Processing {site_name} ({site_id}) device {device_id}…")
            if brute_force:
                df = get_brute_force_readings(token, site_id, device_id, from_date, to_date, step_hours)
            else:
                df = get_readings(token, site_id, device_id, from_date, to_date)

            if df.empty:
                logger.info(f"  → No data for {site_id}/{device_id}")
                continue

            # annotate and collect
            df["farm"]   = site["farm"]
            df["site"]   = site_name
            df["device"] = device_id
            all_dfs.append(df)

    return all_dfs
    
def main():
    parser = argparse.ArgumentParser(
        description="Fetch GroGuru sensor readings for all devices and save to a combined CSV"
    )
    parser.add_argument("-s", "--start", required=True, type=valid_date)
    parser.add_argument("-e", "--end", required=True,   type=valid_date)
    parser.add_argument("-b", "--brute", "--brute-force", dest="brute_force", action="store_true", help="Use brute force fetching (chunked)"
    )
    parser.add_argument("--outdir", "-o", default=".", help="Output directory")
    parser.add_argument("--outfile", "-f",
        help="Filename for combined output (default: groguru_<end>.csv)"
    )
    parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable DEBUG logging"
    )
    parser.add_argument("--chunk-hours", type=int, default=2,
        help="Hours per brute-force chunk (default: 2)")
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="Fetch devices in parallel (default: False)"
    )

    args = parser.parse_args()

    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level,
                        format="%(asctime)s %(levelname)s %(message)s")

    if not args.outfile:
        args.outfile = f"groguru_{args.end.strftime('%Y-%m-%d')}.csv"

    if args.end < args.start:
        parser.error("End date must be on or after start date")

    from_date = args.start
    to_date   = args.end
    step_hours = args.chunk_hours

    token, user_id = authenticate(GROGURU_USERNAME, GROGURU_PASSWORD)
    org_data = get_organization_view(token, user_id)
    if org_data is None:
        logger.error("Could not fetch organization – aborting.")
        sys.exit(1)
    sites    = list_sites_from_org(org_data)

    outdir = Path(args.outdir)
    outdir.mkdir(exist_ok=True)
    outfile = outdir / args.outfile

    reading_method = collect_readings_parallel if args.parallel else collect_readings

    all_dfs = reading_method(
        token, sites, from_date, to_date, brute_force=args.brute_force, step_hours=step_hours
    )

    if not all_dfs:
        logger.info("No data retrieved for any device.")
        sys.exit(0)

    # concatenate all device data into one DataFrame
    combined = pd.concat(all_dfs, ignore_index=True)

    combined.to_csv(outfile, index=False)
    logger.info(f"Wrote {len(combined)} total records to {outfile}")

if __name__ == "__main__":
    main()
