# aquaspy_scraper.py
import requests
import json
import xml.etree.ElementTree as ET
import argparse
from datetime import datetime
from config import AQUASPY_USERNAME, AQUASPY_PASSWORD  # for later expansion

# TODO: Resume season data retrieval code after AquaSpy sensors are active and marked InSeason

BASE_URL = "https://agspy.aquaspy.com/Proxies/SiteService.asmx"

def get_site_metadata(site_id: int) -> dict:
    """
    Fetch site-level metadata from AquaSpy API for a given site ID.
    """
    url = f"{BASE_URL}/GetSiteApiData?siteID={site_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data for site {site_id} — {response.status_code}")

    # The response is XML with a single <string> tag containing JSON
    xml_root = ET.fromstring(response.text)
    raw_json = xml_root.text
    data = json.loads(raw_json)

    if not data.get("Success", False):
        raise Exception(f"AquaSpy returned failure for site {site_id}")

    return data["Data"]  # This contains the actual site metadata


def get_season_data(field_season_id: int) -> dict:
    """
    Fetch full season data (moisture, EC, temperature) for the given season ID.
    """
    url = f"{BASE_URL}/GetSeasonApiData?fieldSeasonID={field_season_id}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch season data — {response.status_code}")

    xml_root = ET.fromstring(response.text)
    raw_json = xml_root.text
    payload = json.loads(raw_json)

    if not payload.get("Success", False):
        raise Exception(f"AquaSpy season call failed — {payload.get('Messages')}")

    return payload["Data"]  # Contains SiteID, FieldSeasonID, MaxReadTimestampUTC, and SeasonData[]


def get_differential_data(field_season_id: int, reference_timestamp: str) -> dict:
    """
    Fetch new season data since the given UTC timestamp (RFC format).
    """
    import urllib.parse
    encoded_time = urllib.parse.quote(reference_timestamp)
    url = f"{BASE_URL}/GetSeasonDifferentialApiData?fieldSeasonID={field_season_id}&referenceTimestamp={encoded_time}"
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception("Failed to fetch differential data")

    xml_root = ET.fromstring(response.text)
    raw_json = xml_root.text
    payload = json.loads(raw_json)

    if not payload.get("Success", False):
        raise Exception(f"Diff fetch failed — {payload.get('Messages')}")

    return payload["Data"]


if __name__ == "__main__":
    import argparse
    from datetime import datetime

    # Optional CLI args for headless mode
    parser = argparse.ArgumentParser(description="AquaSpy API Data Fetcher")
    parser.add_argument("--site", type=int, help="Optional: AquaSpy Site ID")
    parser.add_argument("--season", action="store_true", help="Fetch full season data")
    args = parser.parse_args()

    # Headless mode (CLI args provided)
    if args.site:
        try:
            metadata = get_site_metadata(args.site)
            print(f"\nSite {args.site}: {metadata['SiteDesc']}")
            print(f"  InSeason: {metadata['InSeason']}")
            print(f"  HasEquipment: {metadata['HasEquipment']}")
            print(f"  Customer: {metadata['CustomerName']}")

            if args.season:
                season_id = metadata.get("CurrentFieldSeasonID")
                if season_id:
                    print(f"Fetching full season data for season ID {season_id}...")
                    data = get_season_data(season_id)
                    print(f"  Records returned: {len(data['SeasonData'])}")
                else:
                    print("No active season to fetch data from.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        # Interactive mode (default)
        print("Welcome to the AquaSpy Interactive Fetch Tool")
        try:
            site_id = int(input("Enter a Site ID to fetch metadata: "))
            metadata = get_site_metadata(site_id)
            print(f"\nSite {site_id}: {metadata['SiteDesc']}")
            print(f"  InSeason: {metadata['InSeason']}")
            print(f"  HasEquipment: {metadata['HasEquipment']}")
            print(f"  Customer: {metadata['CustomerName']}")

            if not metadata.get("InSeason"):
                print("This site is not currently in season. No sensor data available.")
            else:
                season_id = metadata.get("CurrentFieldSeasonID")
                print("\nChoose data retrieval mode:")
                print("1. Full season data")
                print("2. Differential data since a date")
                choice = input("Enter choice (1 or 2): ").strip()

                if choice == "1":
                    print(f"Fetching full season data for season ID {season_id}...")
                    data = get_season_data(season_id)
                    print(f"  Records returned: {len(data['SeasonData'])}")
                    print(f"  Latest: {data['MaxReadTimestampUTC']}")
                elif choice == "2":
                    date_str = input("Enter reference timestamp (YYYY-MM-DD HH:MM:SS UTC): ").strip()
                    from datetime import datetime
                    try:
                        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        ref_timestamp = dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")
                        print(f"Fetching differential data since {ref_timestamp}...")
                        diff = get_differential_data(season_id, ref_timestamp)
                        print(f"  Records returned: {len(diff['SeasonData'])}")
                        print(f"  Latest: {diff['MaxReadTimestampUTC']}")
                    except ValueError:
                        print("Invalid date format. Please use 'YYYY-MM-DD HH:MM:SS'")
                else:
                    print("Invalid choice.")
        except Exception as e:
            print(f"Error during interactive session: {e}")



