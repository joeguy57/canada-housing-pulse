-- affordability_inflection.sql

WITH base AS (
    SELECT * FROM {{ ref('stg_housing') }}
),

-- STEP 1: compute the window function per row, BEFORE any grouping happens
with_latest AS (
    SELECT
        city,
        province,
        year_month,
        index_value,
        is_peak_month,
        ANY_VALUE(index_value) OVER (
            PARTITION BY city
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS latest_index_value
    FROM base
),

-- STEP 2: now aggregate — latest_index_value is already a plain column here,
-- not a window function, so GROUP BY is fine
thresholds AS (
    SELECT
        city,
        province,

        MIN(CASE WHEN index_value >= 100 THEN year_month END) AS first_crossed_baseline,
        MIN(CASE WHEN index_value >= 120 THEN year_month END) AS first_crossed_120,
        MIN(CASE WHEN index_value >= 150 THEN year_month END) AS first_crossed_150,
        MIN(CASE WHEN index_value >= 200 THEN year_month END) AS first_doubled,

        MAX(index_value) AS peak_index_value,
        MIN(CASE WHEN is_peak_month THEN year_month END) AS peak_month,

        MAX(year_month) AS latest_month,
        ANY_VALUE(latest_index_value) AS latest_index_value,

        ROUND(
            (ANY_VALUE(latest_index_value) - MAX(index_value)) / MAX(index_value) * 100
        , 1) AS pct_below_peak_now
    FROM with_latest
    GROUP BY city, province
),

with_years AS (
    SELECT
        city,
        province,
        peak_index_value,
        ROUND(peak_index_value - 100, 1) AS peak_rise_from_baseline_pct,
        peak_month,
        latest_month,
        latest_index_value,
        pct_below_peak_now,

        CASE WHEN pct_below_peak_now < -5 THEN TRUE ELSE FALSE END AS is_recovering,
        first_crossed_baseline,
        first_crossed_120,
        first_crossed_150,
        first_doubled,

        CASE
            WHEN first_crossed_baseline IS NOT NULL AND first_crossed_150 IS NOT NULL THEN
                ROUND(DATEDIFF(first_crossed_150, first_crossed_baseline) / 365.25, 1)
        END AS years_baseline_to_150
    FROM thresholds AS t
)

SELECT * FROM with_years
ORDER BY peak_index_value DESC