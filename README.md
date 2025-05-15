# Soil‑Moisture Sensor API Scrapers  
Created by **A.J. Brown**  
Agricultural Data Scientist — CSU Agricultural Water Quality Program  
[Ansley.Brown@colostate.edu](mailto:Ansley.Brown@colostate.edu)

---

## 1 • Project Scope

This repository houses **API-based data fetching tools** for three commercial soil‑moisture platforms:

| Vendor        | API Docs / Swagger | Script |
|---------------|--------------------|--------|
| **Sentek IrriMAX Live v1.9** | <https://irrimaxlive.sentek.com.au/api/docs> | `irrimax_scraper.py` |
| **AquaSpy**   | <https://agspy.aquaspy.com/apioverview> | `aquaspy_scraper.py` *(WIP)* |
| **GroGuru InSites** | <https://groguruinsites.docs.apiary.io/> | `groguru_scraper.py` *(WIP)* |

All scrapers share a common goal: **fetch logger metadata + time‑series moisture data → return a tidy `pandas.DataFrame`** that can be streamed directly into **WISE Pro** (Water Irrigation Scheduling for Efficient Application).

---

## 2 • Why this matters for **WISE Pro**

WISE Pro is an integrated decision‑support platform jointly developed by CSU, USDA‑ARS, and NMSU. It fuses real‑time sensing, machine‑learning data assimilation, and SWAT+/pyFAO56 modeling to generate **actionable irrigation & nutrient recommendations**.  
Automated ingestion of Sentek, AquaSpy, and GroGuru data:

* improves water‑balance forecasts,
* reduces manual file wrangling, and
* enables comparative analytics across hardware vendors.

---

## 3 • Repository Layout
```bash
/code
├── irrimax_scraper.py
├── aquaspy_scraper.py # coming soon
├── groguru_scraper.py # coming soon
├── config_template.py # template to create user-specific config.h
└── config.py # must be created by user and updated with credentials
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

### 4.2 Run a scrape (IrriMAX example)
```bash
python code/irrimax_scraper.py \
  --logger "Soybeans 1" \
  --days-back 7
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

## 5 • Common Features

* **Secure authentication** — credentials isolated in private config files.  
* **Logger discovery** — enumerate available sites/probes before requesting data.  
* **Date‑range queries** — RFC‑3339 / yyyymmddHHMMSS handled automatically.  
* **Returns `pandas.DataFrame`** — ready for in‑memory analytics or other pipelines.  
* Optional **CSV export** or direct write to Postgres/BigQuery (coming soon).

> [!NOTE] 
> Data are returned in the same schema as the vendor provides; unification may be a feature added later.

---

## 6 • Contributing

1. Fork → feature branch → PR.  
2. Follow PEP8; run `black` before committing.  
3. Unit tests live in `tests/`; please add coverage for new endpoints.

---

## 7 • License

GNU General Public License v2.0  
© 2025 Ansley Joseph Brown
