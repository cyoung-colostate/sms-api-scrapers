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

import json  # for debugging
import requests
import datetime
import pandas as pd
import sys
import argparse
from io import StringIO
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

def get_readings(token, site_id, device_id, from_date, to_date):
    print(f"Fetching readings for site {site_id} and device {device_id} from {from_date.date()} to {to_date.date()}...")
    headers = {"Authorization": token}
    params = {
        "fromDate": from_date.strftime("%Y-%m-%d"),
        "toDate": to_date.strftime("%Y-%m-%d"),
        "limit": 1000
    }
    url = f"{BASE_URL}/stem/graph-data/{site_id}/{device_id}/"
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        json_data = response.json()
        graph_data = json_data.get("data", {}).get("graph", {})
        if not graph_data:
            print("No graph data returned.")
            return pd.DataFrame()

        df_flat = flatten_graph_data(graph_data)
        print(df_flat.head())
        return df_flat

    else:
        raise Exception(f"Error fetching readings: HTTP {response.status_code} - {response.text}")

def get_brute_force_readings(token, site_id, device_id, from_date, to_date, step_hours=2):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GroGuru Data Fetcher")
    parser.add_argument("--site", type=str, help="Site ID", required=False)
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)", required=False)
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)", required=False)
    args = parser.parse_args()

    try:
        token, userid = authenticate(GROGURU_EMAIL, GROGURU_PASSWORD)
        org_data = get_organization_view(token, userid)
        sites = list_sites_from_org(org_data)

        if not sites:
            print("No sites found.")
            sys.exit(0)

        if args.site and args.start and args.end:
            selected_site_id = args.site
            matching_sites = [s for s in sites if str(s["siteId"]) == selected_site_id]
            if not matching_sites:
                print("SiteId not found.")
                sys.exit(1)
            twig_id = matching_sites[0]["devices"][0]
            from_date = datetime.datetime.strptime(args.start, "%Y-%m-%d")
            to_date = datetime.datetime.strptime(args.end, "%Y-%m-%d")
            df = get_brute_force_readings(token, selected_site_id, twig_id, from_date, to_date)
            print(df.head())

        else:
            print("Available Sites:")
            for site in sites:
                print(f" - {site['farm']} / {site['name']} (siteId: {site['siteId']})")

            selected_site_id = input("Enter a siteId to fetch readings: ").strip()
            matching_sites = [s for s in sites if str(s["siteId"]) == selected_site_id]
            if not matching_sites:
                print("SiteId not found.")
                sys.exit(1)

            twig_id = matching_sites[0]["devices"][0]
            print(f"Using twigId (deviceId): {twig_id}")
            start_str = input("Enter start date (YYYY-MM-DD): ").strip()
            end_str = input("Enter end date (YYYY-MM-DD): ").strip()

            try:
                from_date = datetime.datetime.strptime(start_str, "%Y-%m-%d")
                to_date = datetime.datetime.strptime(end_str, "%Y-%m-%d")
                if from_date > to_date:
                    raise ValueError("Start date must be before end date.")
            except ValueError as ve:
                print(f"Invalid date format: {ve}")
                sys.exit(1)

            df = get_brute_force_readings(token, selected_site_id, twig_id, from_date, to_date)
            print(df.head())

    except Exception as e:
        print(f"Error: {e}")
