# IrriMAX Live API Scraper
Created by **A.J. Brown**
Agricultural Data Scientist
CSU Agriulctural Water Quality Program
[Ansley.Brown@colostate.edu](mailto:Ansley.Brown@colostate.edu)

## Overview

This project provides a Python-based API scraper for retrieving **soil moisture sensor data** from the **IrriMAX Live API v1.9** by Sentek. The script fetches logger details, retrieves readings for a given time range, and saves the data in a CSV file. 

This effort is part of **WISE Pro** (Water Irrigation Scheduling for Efficient Application), an integrated software platform designed to improve irrigation and nutrient management in cropland agriculture. The goal is to assimilate **real-time soil moisture sensor data** to support **data-driven irrigation decisions**.

IrriMAX Live API Documentation: [https://irrimaxlive.sentek.com.au/api/docs](https://irrimaxlive.sentek.com.au/api/docs)

## Features
- **Authentication via API Key** (secured using `config.py`).
- **Fetch logger details** to identify available soil moisture probes.
- **Retrieve time-series sensor data** in CSV format.
- **Automate data collection** for integration into **WISE Pro**.

## Installation
### **1. Clone the Repository**
```bash
git clone https://github.com/your-repo-name/irrimax-scraper.git
cd irrimax-scraper
```

## Create a Virtual Environment (Optional)
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate      # On Windows
```

## Install Dependencies
```bash
pip install requests
```

## Configure API key in `config.py`
```python
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key
```

# Integration with WISE Pro
Developed for the WISE Pro Project – A collaboration between Colorado State University, USDA-ARS, and New Mexico State University to improve agricultural sustainability and water conservation through an improved irrigation and nutrient management software for agricultural managers.

WISE Pro is a decision support system that integrates sensor data, machine learning, and process-based modeling to optimize irrigation and nutrient application. This scraper automates the ingestion of real-time soil moisture data into WISE Pro’s database, improving forecasting and advisory recommendations.

# License
This project is licensed under the GNU General Public License v2.0.
