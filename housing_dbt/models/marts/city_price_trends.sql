-- city_price_trends.sql
-- One row per city per month with price index, changes and rolling average.
-- This is the primary table feeding the Plotly dashboard

WITH base AS (
    SELECT * FROM {{ ref('stg_housing') }}
),
with_rank AS (
    SELECT
        *,
        -- Rank this month's index value within the city's history
        PERCENT_RANK() OVER(
            PARTITION BY city
            ORDER BY index_value
        ) AS index_percentile,

        -- How many months of conseutive YoY growth
        PERCENT_RANK() OVER(
            PARTITION BY city
            ORDER BY year_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS months_yoy_growth_last_12
    FROM base
)

SELECT * FROM with_rank
ORDER BY city, year_month