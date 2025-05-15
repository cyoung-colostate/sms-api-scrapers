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
The script prints the first few rows of the returned DataFrame; saving to CSV / DB is optional and can be added downstream.

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
