-- stg_housing.sql
-- Silver LOayerL cast_types, filter nulls, rename for clarity.
-- This view is the single source of truth for all mart models.

WITH source AS (
    SELECT * FROM {{ source('housing_pulse', 'nhpi_raw')}}
),

typed AS (
    SELECT
        CAST(year_month AS TIMESTAMP) AS year_month,
        CAST(year AS INT) AS year,
        CAST(month AS INT) AS month,
        quarter,
        city,
        province,
        CAST(index_value AS DOUBLE) AS index_value,
        CAST(yoy_change_pct AS DOUBLE) AS yoy_change_pct,
        CAST(mom_change_pct AS DOUBLE) AS mom_change_pct,
        CAST(rolling_12m_average AS DOUBLE) AS rolling_12m_avg,
        affordability_era,
        CAST(is_peak_month AS BOOLEAN) AS is_peak_month,
        CAST(pct_below_peak AS DOUBLE) AS pct_below_peak,
        CAST(change_since_baseline_pct AS DOUBLE) AS change_since_baseline_pct
    FROM SOURCE
    WHERE index_value IS NOT NULL
    AND city IS NOT NULL
    AND year_month IS NOT NULL
)

SELECT * FROM typed