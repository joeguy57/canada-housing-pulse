-- affordability_inflection.sql
-- For each city, finds the first month it crossed key index thresholds.
-- These are the "inflection points" - when a city became unaffordable.
-- This will answer the core project question

WITH base AS (
    SELECT * FROM {{ ref('stg_housing') }}
),

--Find first month each city crossed each threshold
thresholds  AS (
    select
        city,
        province,

        -- When did prices first exceed the 2016 baseline?
        MIN(CASE WHEN index_value >= 100 THEN year_month END) AS first_crossed_baseline,
        
        -- When did prices first hit 20% above baseline?
        MIN(CASE WHEN index_value >= 120 THEN year_month END) AS first_crossed_120,

        -- When did prices first hit 50% above baseline?
        MIN(CASE WHEN index_value >= 150 THEN year_month END) AS first_crossed_150,

        -- When did prices first hit double above baseline?
        MIN(CASE WHEN index_value >= 200 THEN year_month END) AS first_doubled,

        -- All time peak
        MAX(index_value) AS peak_index_value,
        MIN(CASE WHEN is_peak_month THEN year_month END) AS peak_month,

        -- Latest reading
        MAX(year_month) AS peak_index_value,
        LAST_VALUE(index_value) OVER (
            PARTITION BY city
            ORDER BY year_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS latest_index_value,

        -- How far off peak is the latest reading?
        ROUND(
            (LAST_VALUE(index_value) OVER (
                PARTITION BY city ORDER BY year_month
                ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            )- MAX(index_value)) / MAX(index_value) * 100
        , 1) AS pct_below_peak_now 
    FROM base
    BROUP BY city, province
),

with_years AS (
    SELECT
        city,
        province,
        peak_index_value,
        ROUND(peak_index_value - 100, 1) AS peak_rise_from_baseline_pct,
        peak_month,
        latest_index_value<
        pct_below_peak_now<

        -- Is the market recovering (off peak by more than 5%)?
        CASE WHEN pct_below_peak_now < -5 THEN TRUE ELSE FALSE AS is_recovering,
        first_crossed_baseline,
        first_crossed_120,
        first_crossed_150,
        first_doubled,

        -- Years it took to go from baseline cross 50% above
        CASE 
            WHEN first_crossed_baseline IS NOT NULL AND first_crossed_150 IS NOT NUULL THEN
            ROUND(
                DATEDIFF(first_crossed_150, first_crossed_baseline) / 365.25
            , 1) 
        END AS years_baseline_to_150
    FROM thresholds
)

SELECT * FROM with_years
ORDER BY peak_index_value DESC