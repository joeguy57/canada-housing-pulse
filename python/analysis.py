from db_connect import query_df

def query_biggest_rise_from_baseline():
    """Which city rose the most from the Dec 2016 baseline?"""
    return query_df("""
        SELECT
            city,
            province,
            ROUND(peak_index_value, 1) AS peak_index,
            ROUND(peak_rise_from_baseline_pct, 1) AS pct_rise_from_2016,
            peak_month,
            is_recovering,
            ROUND(pct_below_peak_now, 1) AS pct_below_peak_now
        FROM housing_dbt.housing_pulse_marts.affordability_inflection
        WHERE city != 'Canada (National)'
        ORDER BY peak_index_value DESC
    """)

def query_crossed_150_timeline():
    """When did each city cross 50% above baseline?"""
    return query_df("""
        SELECT
            city,
            province,
            first_crossed_150,
            YEAR(first_crossed_150) AS year_crossed_150,
            ROUND(peak_index_value, 1) AS peak_index,
            years_baseline_to_150
        FROM housing_dbt.housing_pulse_marts.affordability_inflection
        WHERE first_crossed_150 IS NOT NULL
        ORDER BY first_crossed_150
    """)

def query_recovering_cities():
    """Which cities are now recovering (more than 5% off their peak)?"""
    return query_df("""
        SELECT
            city,
            ROUND(peak_index_value, 1) AS peak_index,
            peak_month,
            ROUND(latest_index_value, 1) AS current_index,
            ROUND(pct_below_peak_now, 1) AS pct_below_peak
        FROM housing_dbt.housing_pulse_marts.affordability_inflection
        WHERE is_recovering = TRUE
        ORDER BY pct_below_peak_now ASC
    """)

def query_growth_ranking_by_year(years=(2017, 2020, 2022, 2024), top_n=5):
    """Window-function ranking: top YoY growth cities per year."""
    year_list = ", ".join(str(y) for y in years)
    return query_df(f"""
        SELECT
            city,
            year,
            avg_yoy_change,
            growth_rank_in_year,
            price_rank_in_year
        FROM housing_dbt.housing_pulse_marts.city_rankings
        WHERE year IN ({year_list})
        AND growth_rank_in_year <= {top_n}
        ORDER BY year, growth_rank_in_year
    """)


def query_national_vs_cities(cities=("Toronto", "Vancouver", "Calgary", "Montreal", "Halifax")):
    """Compare each city's premium (or discount) over the national index."""
    city_list = ", ".join(f"'{c}'" for c in cities)
    return query_df(f"""
        WITH national AS (
            SELECT year_month, index_value AS national_index
            FROM housing_dbt.housing_pulse_marts.city_price_trends
            WHERE city = 'Canada (National)'
        ),
        cities AS (
            SELECT city, year_month, index_value
            FROM housing_dbt.housing_pulse_marts.city_price_trends
            WHERE city IN ({city_list})
        )
        SELECT
            c.city,
            c.year_month,
            ROUND(c.index_value, 1) AS city_index,
            ROUND(n.national_index, 1) AS national_index,
            ROUND(c.index_value - n.national_index, 1) AS premium_over_national
        FROM cities c
        JOIN national n ON c.year_month = n.year_month
        ORDER BY c.city, c.year_month
    """)


if __name__ == "__main__":
    print("=== Biggest rise from baseline ===")
    print(query_biggest_rise_from_baseline().head(10).to_string(index=False))
    print("\n=== Crossed 150 timeline ===")
    print(query_crossed_150_timeline().to_string(index=False))
    print("\n=== Recovering cities ===")
    print(query_recovering_cities().to_string(index=False))
    print("\n=== Growth ranking by year (top 5) ===")
    print(query_growth_ranking_by_year().to_string(index=False))
    print("\n=== National vs highlight cities (sample) ===")
    print(query_national_vs_cities().head(10).to_string(index=False))