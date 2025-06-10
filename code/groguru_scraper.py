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

import os
import requests
import datetime
import pandas as pd
import sys
import argparse
import config  # Contains GROGURU_EMAIL and GROGURU_PASSWORD

# === CONFIGURABLE CREDENTIALS ===
GROGURU_EMAIL = config.GROGURU_USERNAME
GROGURU_PASSWORD = config.GROGURU_PASSWORD

# === CONSTANTS ===
BASE_URL = "https://api.groguru.com"
LOGIN_ENDPOINT = f"{BASE_URL}/user/signin"
ORG_VIEW_ENDPOINT = f"{BASE_URL}/org/view/{{user_id}}"
GRAPH_DATA_ENDPOINT = f"{BASE_URL}/stem/graph-data/{{siteId}}/{{deviceId}}/"

def authenticate(email, password):
    """Authenticate with the GroGuru API and return a token and user ID."""
    print("Authenticating with GroGuru API...")
    payload = {"email": email, "password": password}
    response = requests.post(LOGIN_ENDPOINT, json=payload)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print(f"Login successful. User: {data['data']['username']}")
            return data['data']['sessionToken'], data['data']['id']
        else:
            print("Login failed. Message:", data.get("message", "No message returned."))
            sys.exit(1)
    else:
        print(f"Login failed. HTTP {response.status_code} - {response.text}")
        sys.exit(1)

def get_organization_view(token, userid):
    """Retrieve the organization view data for the authenticated user."""
    print("Fetching organization view...")
    headers = {"Authorization": token}
    response = requests.get(ORG_VIEW_ENDPOINT.format(user_id=userid), headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            print("Successfully fetched organization data.")
            return data["data"]
        else:
            print("Failed to retrieve organization data:", data.get("message", "No message."))
    else:
        print(f"Failed to get organization view. HTTP {response.status_code} - {response.text}")
    return None

def list_sites_from_org(org_data):
    """Flatten and extract site and device information from organization data."""
    print("Extracting sites and devices from organization data...")
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
        print("Unexpected format in org view response.")
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
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching raw JSON: HTTP {response.status_code} - {response.text}")

def get_readings(token, site_id, device_id, from_date, to_date):
    """Fetch flattened sensor readings DataFrame for a site/device/date range."""
    print(f"Fetching readings for site {site_id} and device {device_id} from {from_date.date()} to {to_date.date()}...")
    json_data = get_raw_json(token, site_id, device_id, from_date, to_date)
    graph_data = json_data.get("data", {}).get("graph", {})
    if not graph_data:
        print("No graph data returned.")
        return pd.DataFrame()
    df_flat = flatten_graph_data(graph_data)
    return df_flat

def get_brute_force_readings(token, site_id, device_id, from_date, to_date, step_hours=2):
    """Repeatedly call `get_readings` over 2-hour intervals to overcome data limits."""
    print(f"Brute force fetching from {from_date} to {to_date} in {step_hours}-hour chunks...")
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
            print(f"Warning: Failed to fetch from {current_start} to {current_end}: {e}")
        current_start = current_end

    if not all_chunks:
        print("No data retrieved.")
        return pd.DataFrame()

    merged_df = (
        pd.concat(all_chunks)
        .drop_duplicates(subset="timestamp")
        .sort_values("timestamp")
        .reset_index(drop=True)
    )

    print(f"Retrieved {len(merged_df)} rows total.")
    return merged_df

def main():
    parser = argparse.ArgumentParser(
        description="Fetch GroGuru sensor readings for all devices and save to a combined CSV"
    )
    parser.add_argument("--start", "-s", required=True, help="Start date in YYYY-MM-DD")
    parser.add_argument("--end", "-e", required=True, help="End date in YYYY-MM-DD")
    parser.add_argument(
        "--brute", "-b", action="store_true", help="Use brute force fetching (chunked)"
    )
    parser.add_argument("--outdir", "-o", default=".", help="Output directory")
    parser.add_argument("--outfile", "-f",
        help="Filename for combined output (default: groguru_<end>.csv)"
    )

    args = parser.parse_args()

    if not args.outfile:
        args.outfile = f"groguru_{args.end}.csv"
    
    from_date = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    to_date   = datetime.datetime.strptime(args.end,   "%Y-%m-%d")

    token, user_id = authenticate(config.GROGURU_USERNAME, config.GROGURU_PASSWORD)
    org_data = get_organization_view(token, user_id)
    sites    = list_sites_from_org(org_data)

    os.makedirs(args.outdir, exist_ok=True)

    all_dfs = []  # <-- collect here

    for site in sites:
        site_id   = site["siteId"]
        site_name = site["name"]
        for device_id in site["devices"]:
            print(f"Processing {site_name} ({site_id}) device {device_id}…")
            if args.brute:
                df = get_brute_force_readings(token, site_id, device_id, from_date, to_date)
            else:
                df = get_readings(token, site_id, device_id, from_date, to_date)

            if df.empty:
                print(f"  → No data for {site_id}/{device_id}")
                continue

            # annotate and collect
            df["farm"]   = site["farm"]
            df["site"]   = site_name
            df["device"] = device_id
            all_dfs.append(df)

    if not all_dfs:
        print("No data retrieved for any device.")
        sys.exit(0)

    # concatenate all device data into one DataFrame
    combined = pd.concat(all_dfs, ignore_index=True)

    out_path = os.path.join(args.outdir, args.outfile)
    combined.to_csv(out_path, index=False)
    print(f"Wrote {len(combined)} total records to {out_path}")

if __name__ == "__main__":
    main()
