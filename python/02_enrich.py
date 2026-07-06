import pandas as pd
import numpy as np

df = pd.read_csv("data/nhpi_clean.csv", parse_dates=["year_month"])
print(f"Loaded {len(df)} rows across {df["city"].nunique()} cities")

# Year over Year Cahnge
df = df.sort_values(["city", "year_month"])

df["yoy_cchange_pct"] = (
    df.groupby("city")["index_value"]
    .pct_change(periods=12)
    .mul(100)
    .round(2)
)

# Month Over Month Change
df["mom_change_pct"] = (
    df.groupby("city")["index_value"]
    .pct_change(periods=1)
    .mul(100)
    .round(2)
)

# Rolling 12 month Average
df["rolling_12m_average"] = (
    df.groupby("city")["index_value"]
    .transform(lambda x: x.rolling(12, min_periods=6).mean())
    .round(2)
)

# Affordability Era Classification
def affordability_era(index_val):
    if pd.isna(index_val):
        return "Unknown"
    if index_val < 80:
        return "Pre-boom (very affordable)"
    if index_val < 100:
        return "Affordable (below 2016 baseline)"
    if index_val < 120:
        return "Moderate (0-20% above baseline)"
    if index_val < 150:
        return "Elevated (20 - 50% above baseline)"
    if index_val < 200:
        return "Expensive (50 - 100% above baseline)"
    return "Crisis (doubled from baseline)"

df["affordability_era"] = df["index_value"].apply(affordability_era)

# Peak Detection Flag
city_peaks = (
    df.groupby("city")["index_value"]
    .transform("max")   
)
df["is_peak_month"] = (df["index_value"] == city_peaks).astype(int)

# Distance from peak
df["pct_below_peak"] = (
    (df["index_value"] - city_peaks) / city_peaks * 100
).round(2)

# Index Change Since 2016 Baseline
df["change_since_baseline_pct"] = (df["index_value"] - 100).round(2)

# Save
df.to_csv("data/nhpi_enriched.csv", index= False)

print(f"\n Enriched shape: {df.shape}")

# Quick Summary
summary = df.groupby("city").agg(
    latest_index = ("index_value", "last"),
    peak_index = ("index_value", "max")
    avg_yoy = ("yoy_change_pct", "mean"),
).round(2).sort_values("latest_index", ascending= False)

print(f"\nCity summary (sorted by latest index):\n{summary.head(10)}")
print(f"\nSaved --> data/nhpi_enriched.csv ")