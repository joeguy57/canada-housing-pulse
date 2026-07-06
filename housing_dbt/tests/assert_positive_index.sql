SELECT city, year_month, index_value
FROM {{ ref('stg_housing') }}
where index_value <= 0