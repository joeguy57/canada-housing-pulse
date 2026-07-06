-- city_rankings.sql
-- Annual summary ranking all cities by price growth, volatility, and recovery.
-- Great for "which city is worst / best" narrative.

WITH trends AS (
    SELECT * FROM {{ ref('city_price_trends') }}
),
annual AS (
    SELECT
        city,
        province,
        year,
        ROUND(AVG(index_value), 1) AS avg_index,
        ROUND(AVG(yoy_change_pct), 1) AS avg_yoy_change,
        ROUND(MAX(index_value), 1) AS peak_index_in_year,
        ROUND(MIN(index_value), 1) AS trough_index_in_year,
        ROUND(MAX(index_value) - MIN(index_value), 1) AS intra_year_range
    FROM trends
    WHERE year >= 2010
    GROUP BY city, province, year
)

SELECT
    city,
    province,
    year,
    avg_index,
    avg_yoy_change,
    peak_index_in_year,
    trough_index_in_year,
    intra_year_range,

    -- Rank by growth rate within each year
    RANK() OVER (
        PARTITION BY year
        ORDER BY avg_yoy_change DESC         
    ) AS growth_rank_in_year
FROM annual
ORDER BY year DESC, avg_index DESC