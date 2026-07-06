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

