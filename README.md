# CanadaHousingPulse
> Which Canadian cities became unaffordable — and exactly when did it happen?
Using 40+ years of Statistics Canada New Housing Price Index data
across 27 Canadian cities, this project builds a full data pipeline
to pinpoint housing affordability inflection points by city.
## Key Findings
- Ottawa-Gaineau crossed 150 on the index (50% above Dec 2016 baseline) first, in April 2021.
- Montreal peaked at 159.4 on the index in [Month Year] and has since fallen 982.1%
- Edmonton is showing the most pronounced correction of any major city, sitting 9.1% below its all-time peak as of October 2007.
- The national index peaked at 40.8 in [Month Year] — 13.9 above the 2016 baseline
## Dashboard Preview
[→ View interactive dashboard](dashboard/housing_pulse.html)
## Stack
| Layer | Tool |
|---|---|
| Data Cleaning | Python + pandas |
| Feature Engineering | Python + numpy |
| Cloud Storage | Databricks Community Edition + Delta Lake |
| Transformations | dbt (staging + 3 mart models) |
| Analytics & Dashboard | Python querying dbt marts directly via the Databricks SQL Connector |
| Visualization | Plotly (interactive HTML) |
## Architecture Note
Both the analytical queries (`python/analysis.py`) and the dashboard (`python/03_dashboard.py`)
read live from `housing_pulse_marts` — the same tables validated by `dbt test`. There is no
separate CSV path feeding the dashboard, so a failing dbt test blocks bad data before it
ever reaches a chart.
## Data Source
Statistics Canada — New Housing Price Index (Table 18-10-0205-01)
Direct CSV download — no account required:
https://www150.statcan.gc.ca/n1/tbl/csv/18100205-eng.zip
## How to Run
1. Clone this repo
2. `python -m venv venv && source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `python python/download_data.py` (or download manually — see below)
5. `python python/01_clean.py`
6. `python python/02_enrich.py`
7. Upload `data/nhpi_enriched.csv` to Databricks as `housing_pulse.nhpi_raw`
8. `cd housing_dbt && dbt run && dbt test`
9. Create a `.env` file with your `DATABRICKS_SERVER_HOSTNAME`, `DATABRICKS_HTTP_PATH`,
and `DATABRICKS_TOKEN`
10. `python python/analysis.py` — prints the headline findings
11. `python python/03_dashboard.py` — builds `dashboard/housing_pulse.html`
12. Open `dashboard/housing_pulse.html` in your browser