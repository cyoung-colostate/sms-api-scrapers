# Soil‑Moisture Sensor API Scrapers  
Created by **A.J. Brown**  
Agricultural Data Scientist — CSU Agricultural Water Quality Program  
[Ansley.Brown@colostate.edu](mailto:Ansley.Brown@colostate.edu)

---

## 1 • Project Scope

This repository houses **API-based data fetching tools** for three commercial soil‑moisture platforms:

| Vendor              | API Docs from Company                                       | Script              | Reference Notes                           |
|---------------------|----------------------------------------------------------|---------------------|--------------------------------------------|
| **Sentek IrriMAX**  | [Irrimax Site](https://irrimaxlive.sentek.com.au/api/docs)  | [`irrimax_scraper.py`](code/irrimax_scraper.py) | [View Notes](docs/irrimax_api_info.md)       |
| **AquaSpy** *(Hold)*| [AquaSpy Site](https://agspy.aquaspy.com/apioverview)   | [`aquaspy_scraper.py`](code/aquaspy_scraper.py) | [View Notes](docs/agspy_api_info.md)       |
| **GroGuru InSites** | [GroGuru Site](https://groguruinsites.docs.apiary.io/)        | [`groguru_scraper.py`](code/groguru_scraper.py) | [View Notes](docs/groguru_info.md)         |


All scrapers share a common goal: **fetch logger metadata + time‑series moisture data → return a tidy `pandas.DataFrame`** that can be streamed directly into **WISE Pro** (Water Irrigation Scheduling for Efficient Application).

> [!IMPORTANT]
> Before using a scraper, please review its corresponding markdown file in the `/docs/` folder, which are linked in the table above. These files contain important notes about API limitations, usage, and other relevant information.

---
## 📚 Table of Contents
- [1 • Project Scope](#1•project-scope)
- [2 • How This Supports WISE Pro](#2•how-this-supports-wisepro)
- [3 • Repository Layout](#3•repository-layout)
- [4 • Quick Start](#4•quickstart)
  - [4.1 • Configure Secrets](#41•configure-secrets)
  - [4.2 • Run a scrape via console command (IrriMAX example)](#42-run-a-scrape-via-console-command-irrimax-example)
  - [4.3 • Automated Cloud Deployment](#43•-example-usage-on-a-linux-server-automated-cloud-deployment)
    - [4.3.1 • IrriMAX](#431•irrimax-live-via-get_readings)
    - [4.3.2 • GroGuru](#432•groguru-insites-via-get_brute_force_readings)
    - [4.3.3 • AquaSpy (On-Hold)](#433--aquaspy-agspy-api-metadata-only)
- [5 • Common Features](#5•commonfeatures)
- [6 • Known API Limitations by Vendor](#6•known-api-limitations-by-vendor)
- [7 • Contributing](#7•contributing)
- [8 • License](#8•license)


## 2 • How This Supports WISE Pro

WISE Pro is an integrated decision‑support platform jointly developed by CSU, USDA‑ARS, and NMSU. It fuses real‑time sensing, machine‑learning data assimilation, and SWAT+/pyFAO56 modeling to generate **actionable irrigation & nutrient recommendations**.  
Automated ingestion of Sentek, AquaSpy, and GroGuru data:

* improves water‑balance forecasts,
* reduces manual file wrangling, and
* enables comparative analytics across hardware vendors.

---

## 3 • Repository Layout
```bash
sms-api-scrapers/
│
├── README.md               # Project overview and usage instructions
├── requirements.txt        # Shared Python dependencies
├── login_info.md           # Manual record of usernames/passwords (not committed)
├── LICENSE                 # GNU GPL v2.0 license
├── .gitignore              # Prevents secrets and compiled files from being tracked
│
├── code/                   # All executable scraping scripts and configuration
│   ├── irrimax_scraper.py       # Sentek IrriMAX API scraper
│   ├── aquaspy_scraper.py       # AquaSpy API scraper (partially functional)
│   ├── groguru_scraper.py       # GroGuru InSites API scraper
│   ├── config_template.py       # Safe starter config file to copy and edit
│   ├── config.py                # Local, untracked config with real credentials
│   └── __pycache__/             # Compiled Python bytecode (ignored)
│
└── docs/                   # API documentation and notes (not for execution)
    ├── irrimax_api_info.md       # IrriMAX v1.9 API documentation summary
    ├── agspy_api_info.md         # AquaSpy AgSpy API limitations + usage notes
    ├── groguru_info.md           # Usage notes and walkthrough for GroGuru API
    └── groguruinsites.apib       # Original GroGuru API Blueprint (APIary format)

```

---

## 4 • Quick Start

```bash
# clone & create env
git clone https://github.com/your-org/soil‑moisture‑scrapers.git
cd soil‑moisture‑scrapers
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate

# install shared deps
pip install -r requirements.txt
```

### 4.1 Configure Secrets  
1. Create your private config file (one place for every platform’s credentials):  
   ```bash
   cp code/config_template.py code/config.py
   ```

2. Add your credentials / API keys.

3. Do not commit `config.py` - it is already listed in `.gitignore`

### 4.2 Run a scrape via console command (IrriMAX example)
```bash
>python irrimax_scraper.py
Choose an option:
1. List available loggers
2. Fetch readings for a specific logger
Enter 1 or 2: 2
Enter logger name (case-sensitive): 8A_8
Enter start date (YYYY-MM-DD): 2024-06-10
Enter end date (YYYY-MM-DD): 2024-10-15

Fetching data for logger: 8A_8 (2024-06-10 to 2024-10-15)...
             Date Time      V1      V2     A1(5)     S1(5)  ...    S8(75)    T8(75)    A9(85)    S9(85)  T9(85)
0  2024/06/10 00:00:00  13.735  13.474  16.63106  379.6608  ...  844.3812  17.04999  40.48423  4438.727   16.72
1  2024/06/10 00:30:00  13.769  -1.000  16.62494  376.4792  ...  844.4537  17.04999  40.48423  4438.727   16.72
2  2024/06/10 01:00:00  13.787  -1.000  16.62494  378.4209  ...  844.3812  17.01999  40.49162  4439.438   16.72
3  2024/06/10 01:30:00  13.783  -1.000  16.58220  373.6646  ...  844.0801  16.95001  40.46944  4437.237   16.75
4  2024/06/10 02:00:00  13.707  -1.000  16.60052  373.4932  ...  844.3039  17.00000  40.49162  4422.122   16.72

[5 rows x 30 columns]
```
The script prints the first few rows of the returned DataFrame

### 4.3 • Example Usage on a Linux Server (Automated Cloud Deployment)

Your `irrimax_scraper.py` script supports both interactive use and programmatic importing. For cloud deployment (e.g., using `cron`), you can create a simple runner script to automate daily data pulls.

> [!IMPORTANT] 
> Be sure your config.py file is properly populated and present in the same directory or Python path when the script runs.

#### 4.3.1 • IrriMAX Live via `get_readings()`

To automate data ingestion:

1. **Create a runner script (e.g., `daily_pull.py`):**

```python
from irrimax_scraper import get_readings
import datetime
import pandas as pd

# Define logger and time window
logger_name = "Soybeans 1"
to_date = datetime.datetime.utcnow()
from_date = to_date - datetime.timedelta(days=1)

# Fetch and save data
df = get_readings(logger_name, from_date, to_date)

if not df.empty:
    out_path = f"/home/user/data/{logger_name.replace(' ', '_')}_{from_date:%Y%m%d}.csv"
    df.to_csv(out_path, index=False)
```

2. Add the task to your crontab (`crontab -e`):

```cron
0 3 * * * /usr/bin/python3 /home/user/scripts/daily_pull.py >> /home/user/logs/irrimax.log 2>&1
```

This will:

- Run the script every day at 3:00 AM

- Save a CSV to /home/user/data/

- Log all output and errors to /home/user/logs/irrimax.log


#### 4.3.2 • GroGuru InSites via `get_brute_force_readings()`

To automate GroGuru data collection from a known site:

1. **Create a runner script (e.g., `groguru_pull.py`):**

```python
from groguru_scraper import authenticate, get_organization_view, list_sites_from_org, get_brute_force_readings
import datetime
import config

# Authenticate and fetch organization structure
token, userid = authenticate(config.GROGURU_USERNAME, config.GROGURU_PASSWORD)
org_data = get_organization_view(token, userid)
sites = list_sites_from_org(org_data)

# Choose a specific siteId and deviceId (twigId is auto-selected as first device)
site_id = "11697"  # Replace with your actual GroGuru siteId
device_id = sites[0]["devices"][0]  # Automatically selects the first twigId

# Define date range
to_date = datetime.datetime.utcnow()
from_date = to_date - datetime.timedelta(days=1)

# Fetch data using brute-force workaround
df = get_brute_force_readings(token, site_id, device_id, from_date, to_date)

# Save to CSV
if not df.empty:
    out_path = f"/home/user/data/groguru_{site_id}_{from_date:%Y%m%d}.csv"
    df.to_csv(out_path, index=False)
```
2. **Add the task to your crontab (`crontab -e`):**

```cron
30 3 * * * /usr/bin/python3 /home/user/scripts/groguru_pull.py >> /home/user/logs/groguru.log 2>&1
```

This will:

- Run daily at 3:30 AM

- Save a GroGuru CSV with the last 24 hours of data

- Log output/errors to /home/user/logs/groguru.log

> [!NOTE]
> The GroGuru API limits each request to 5 data points. get_brute_force_readings() uses a looping strategy with 2-hour windows to stitch together full time series.

#### 4.3.3 • AquaSpy AgSpy API (Metadata Only)

The `aquaspy_scraper.py` script retrieves **site metadata** only. Seasonal data is unavailable unless AquaSpy probes are actively deployed and marked "InSeason" in the AquaSpy portal.

Example run:

```bash
> python aquaspy_scraper.py
Site 33853: Farm 1 - 4D - Block II
  InSeason: False
  HasEquipment: False
  Customer: Farm 1
```
Seasonal data endpoints (`GetSeasonApiData`, `GetSeasonDifferentialApiData`) will return empty or error if the site has no `CurrentFieldSeasonID`. This integration is paused until sensor deployment.

## 5 • Common Features

* **Secure authentication** — credentials isolated in private config files.  
* **Logger discovery** — enumerate available sites/probes before requesting data.  
* **Date‑range queries** — RFC‑3339 / yyyymmddHHMMSS handled automatically.  
* **Returns `pandas.DataFrame`** — ready for in‑memory analytics or other pipelines.  
* Optional **CSV export** or direct write to Postgres/BigQuery (coming soon).

> [!NOTE] 
> Data are returned in the same schema as the vendor provides; unification may be a feature added later.

## 6 • Known API Limitations by Vendor

| Vendor       | Limitation                                                                 |
|--------------|----------------------------------------------------------------------------|
| **AquaSpy**  | Requires hardcoded `siteID`s; no endpoint to list all available sites.     |
|              | No seasonal data if `InSeason = False`. Only metadata retrieval possible.  |
| **GroGuru**  | 5-point limit per request; requires looping workaround for full time series. |
| **IrriMAX**  | CSV parsing may fail silently for malformed timestamps.                    |

---

## 7 • Contributing

1. Fork → feature branch → PR.  
2. Follow PEP8; run `black` before committing.  
3. Unit tests live in `tests/`; please add coverage for new endpoints.

---

## 8 • License

GNU General Public License v2.0  
© 2025 Ansley Joseph Brown
