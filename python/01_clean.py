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

# REF_DATE comes as "2024-01" — convert to proper date
df["year_month"] = pd.to_datetime(df["year_month"], format="%Y-%m")
df["year"] = df["year_month"].dt.year
df["month"] = df["year_month"].dt.month
df["quarter"] = df["year_month"].dt.to_period("Q").astype(str)

# Keep only the "Total (house and land)" index — the headline measure
df = df[df["index_type"] == "Total (house and land)"].copy()
# Remove rows flagged as unreliable by StatCan
df = df[df["data_quality_flag"].isna() | (df["data_quality_flag"] == "")]
# Convert index value to numeric
df["index_value"] = pd.to_numeric(df["index_value"], errors="coerce")
# Drop rows with no value
df = df.dropna(subset=["index_value"])

print(f"\nAfter filtering: {df.shape}")

# Standardize city names — StatCan uses long CMA names
city_name_map = {
    "Canada": "Canada (National)",
    "Calgary, Alberta": "Calgary",
    "Edmonton, Alberta": "Edmonton",
    "Vancouver, British Columbia": "Vancouver",
    "Victoria, British Columbia": "Victoria",
    "Kelowna, British Columbia": "Kelowna",
    "Saskatoon, Saskatchewan": "Saskatoon",
    "Regina, Saskatchewan": "Regina",
    "Winnipeg, Manitoba": "Winnipeg",
    "Hamilton, Ontario": "Hamilton",
    "Toronto, Ontario": "Toronto",
    "Ottawa-Gatineau, Ontario part, Ontario/Quebec": "Ottawa-Gatineau",
    "Oshawa, Ontario": "Oshawa",
    "London, Ontario": "London",
    "Windsor, Ontario": "Windsor",
    "Montréal, Quebec": "Montreal",
    "Québec, Quebec": "Quebec City",
    "Sherbrooke, Quebec": "Sherbrooke",
    "Saguenay, Quebec": "Saguenay",
    "Trois-Rivières, Quebec": "Trois-Rivieres",
    "Moncton, New Brunswick": "Moncton",
    "Saint John, New Brunswick": "Saint John",
    "Halifax, Nova Scotia": "Halifax",
}
df["city"] = df["city"].map(city_name_map).fillna(df["city"])
# Add province column
province_map = {
    "Calgary": "Alberta",
    "Edmonton": "Alberta",
    "Vancouver": "British Columbia",
    "Victoria": "British Columbia",
    "Kelowna": "British Columbia",
    "Saskatoon": "Saskatchewan",
    "Regina": "Saskatchewan",
    "Winnipeg": "Manitoba",
    "Hamilton": "Ontario",
    "Toronto": "Ontario",
    "Ottawa-Gatineau": "Ontario/Quebec",
    "Oshawa": "Ontario",
    "London": "Ontario",
    "Windsor": "Ontario",
    "Montreal": "Quebec",
    "Quebec City": "Quebec",
    "Sherbrooke": "Quebec",
    "Saguenay": "Quebec",
    "Trois-Rivieres": "Quebec",
    "Moncton": "New Brunswick",
    "Saint John": "New Brunswick",
    "Halifax": "Nova Scotia",
    "Canada (National)": "National",
}
df["province"] = df["city"].map(province_map).fillna("Other")

# Data Shape
print(f"Shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nIndex types: \n{df['index_type'].value_counts()}")
print(f"\nCities:\n{df['city'].value_counts()}")
print(f"\Provinces:\n{df['province'].value_counts()}")
print(f"\nDate range: {df['year_month'].min()} -> {df['year_month'].max()}")
print(f"\nStatus flags:\n{df['data_quality_flag'].value_counts(dropna=False)}")

final_cols = [
    "year_month", "year", "month", "quarter", "city", "province", "index_value"
]

df = df[final_cols].sort_values(["city", "year_month"]).reset_index(drop=True)

print(f"\nClean Shape: {df.shape}")
print(f"\nCities: {df["city"].nunique()}")
print(f"\nDate range: {df["year_month"].min()} -> {df["year_month"].max()}")
print(f"\nSample:\n{df.head(10)}")

df.to_csv("data/nhpi_clean.csv", index=False)
print("\n Saved -> data/nhpi_clean.csv")
