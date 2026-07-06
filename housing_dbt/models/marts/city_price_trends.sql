WITH base AS (
    SELECT * FROM {{ ref('stg_housing') }}
),

with_yoy_flag AS (
    SELECT
        *,
        -- Was this month's index higher than the same month last year?
        CASE
            WHEN index_value > LAG(index_value, 12) OVER (
                PARTITION BY city ORDER BY year_month
            ) THEN 1
            ELSE 0
        END AS had_yoy_growth
    FROM base
),

with_rank AS (
    SELECT
        *,
        -- Rank this month's index value within the city's history
        PERCENT_RANK() OVER (
            PARTITION BY city
            ORDER BY index_value
        ) AS index_percentile,

        -- Count of YoY-growth months within the trailing 12-month window
        SUM(had_yoy_growth) OVER (
            PARTITION BY city
            ORDER BY year_month
            ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
        ) AS months_yoy_growth_last_12
    FROM with_yoy_flag
)

SELECT * FROM with_rank
ORDER BY city, year_month