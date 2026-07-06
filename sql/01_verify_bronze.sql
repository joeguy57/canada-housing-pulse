SELECT
    COUNT(*) AS TOTAL_ROWS,
    COUNT(DISTINCT CITY) AS CITIES,
    MIN(YEAR_MONTH) AS EARLIEST,
    MAX(YEAR_MONTH) AS LATEST,
    ROUND(AVG(INDEX_VALUE), 1) AS AVG_INDEX
FROM nhpi_raw

SELECT
    city,
    COUNT(*) AS months_of_data,
    ROUND(MIN(index_value), 1) AS min_index,
    ROUND(MAX(index_value), 1) AS max_index,
    ROUND(MAX(index_value) - MIN(index_value), 1) AS total_rise
FROM nhpi_raw
GROUP BY city