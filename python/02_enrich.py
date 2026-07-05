import pandas as pd
import numpy as np

df = pd.read_csv("data/nhpi_clean.csv", parse_dates=["year_month"])
print(f"Loaded {len(df)} rows across {df["city"].nunique()} cities")