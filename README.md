# ■ CanadaHousingPulse
> Which Canadian cities became unaffordable — and exactly when did it happen?
Built on 40+ years of Statistics Canada New Housing Price Index data
covering 27 Canadian cities.
## Stack
- Python (pandas, plotly) — cleaning, enrichment, interactive dashboard
- Databricks Community Edition — Delta Lake storage
- dbt — staging and mart model transformations
- Spark SQL — inflection point analysis and city rankings
## Data Source
Statistics Canada — New Housing Price Index, Table 18-10-0205-01
Direct CSV download (no account required):
https://www150.statcan.gc.ca/n1/tbl/csv/18100205-eng.zip
## Status
■ In progress