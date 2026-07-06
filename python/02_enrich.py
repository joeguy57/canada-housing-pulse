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
