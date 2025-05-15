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
from io import StringIO
import config  # Contains GROGURU_EMAIL and GROGURU_PASSWORD

# === CONFIGURABLE CREDENTIALS ===
GROGURU_EMAIL = config.GROGURU_USERNAME
GROGURU_PASSWORD = config.GROGURU_PASSWORD

# === CONSTANTS ===
BASE_URL = "https://api.groguru.com"
LOGIN_ENDPOINT = f"{BASE_URL}/user/signin"
ORG_VIEW_ENDPOINT = f"{BASE_URL}/org/view/{{user_id}}"
READINGS_ENDPOINT = f"{BASE_URL}/site/data"


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
    """Extract and flatten site information from org response."""
    sites = []
    try:
        for farm in org_data.get("children", []):
            for site in farm.get("sites", []):
                sites.append({
                    "farm": farm.get("name"),
                    "name": site.get("name"),
                    "siteId": site.get("siteId"),
                    "id": site.get("id")
                })
    except KeyError:
        print("Unexpected format in org view response.")
    return sites


def get_readings(token, site_id, from_date, to_date):
    """Fetch GroGuru sensor readings for a specific site and date range."""
    print(f"Fetching readings for site {site_id} from {from_date.date()} to {to_date.date()}...")
    headers = {"Authorization": token}
    payload = {
        "siteId": site_id,
        "fromDate": from_date.strftime("%Y-%m-%dT00:00:00.000Z"),
        "toDate": to_date.strftime("%Y-%m-%dT23:59:59.000Z"),
    }
    response = requests.post(READINGS_ENDPOINT, headers=headers, json=payload)

    if response.status_code == 200:
        json_data = response.json()
        if not json_data.get("data"):
            print("No data returned.")
            return pd.DataFrame()

        df = pd.DataFrame(json_data["data"])
        print(df.head())
        return df
    else:
        raise Exception(f"Error fetching readings: HTTP {response.status_code} - {response.text}")


if __name__ == "__main__":
    try:
        token, userid = authenticate(GROGURU_EMAIL, GROGURU_PASSWORD)
        org_data = get_organization_view(token, userid)

        sites = list_sites_from_org(org_data)
        print("Available Sites:")
        for site in sites:
            print(f" - {site['farm']} / {site['name']} (siteId: {site['siteId']}, id: {site['id']})")

        if not sites:
            print("No sites found.")
            sys.exit(0)

        selected_site = input("Enter a siteId to fetch readings: ").strip()
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

        df = get_readings(token, selected_site, from_date, to_date)

    except Exception as e:
        print(f"Error: {e}")
