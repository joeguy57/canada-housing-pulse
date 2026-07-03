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
