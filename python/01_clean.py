import pandas as pd
import numpy as np

df = pd.read_csv("data/nhpi_raw.csv", encoding="utf-8", low_memory=False)

# Data Shape
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nIndex types: \n{df['New housing price indexes'].value_counts()}")
print(f"\nCities:\n{df['GEO'].value_counts()}")
print(f"\nDate range: {df['REF_DATE'].min()} -> {df['REF_DATE'].max()}")
print(f"\nStatus flags:\n{df['STATUS'].value_counts(dropna=False)}")


df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace(r"[^a-z0-9_]", "", regex=True)
)

df = df.rename(columns = {
    "ref_date": "year_month",
    "geo": "city",
    "new_housing_price_indexes": "index_type",
    "value": "index_value",
    "status": "data_quality_flag",
})

# Data Shape
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nIndex types: \n{df['index_type'].value_counts()}")
print(f"\nCities:\n{df['city'].value_counts()}")
print(f"\nDate range: {df['year_month'].min()} -> {df['year_month'].max()}")
print(f"\nStatus flags:\n{df['data_quality_flag'].value_counts(dropna=False)}")