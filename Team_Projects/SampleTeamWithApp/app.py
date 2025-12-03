#!/usr/bin/env python3
"""
World Bank Labor Force Analysis - Streamlit App

This Streamlit app displays an interactive chart showing labor force
participation rates by region over time.

Usage:
    streamlit run app.py

Prerequisites:
    Run load_data.py first to populate the DuckDB database.
"""

import streamlit as st
import duckdb
import altair as alt
from pathlib import Path


# Configuration
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "worldbank.duckdb"


def check_database_exists():
    """Check if the database exists and has data."""
    if not DB_PATH.exists():
        return False
    try:
        conn = duckdb.connect(str(DB_PATH), read_only=True)
        count = conn.execute("SELECT COUNT(*) FROM indicator_with_region").fetchone()[0]
        conn.close()
        return count > 0
    except Exception:
        return False


def get_regional_data(selected_regions=None, year_range=None):
    """Query regional averages from DuckDB."""
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    
    # Build the query with optional filters
    query = """
        SELECT
            region,
            year,
            AVG(value) AS avg_participation_rate,
            COUNT(DISTINCT country_code) AS num_countries
        FROM indicator_with_region
        WHERE region != 'Unknown'
          AND region IS NOT NULL
          AND region != ''
    """
    
    if selected_regions:
        regions_str = ", ".join([f"'{r}'" for r in selected_regions])
        query += f" AND region IN ({regions_str})"
    
    if year_range:
        query += f" AND year >= {year_range[0]} AND year <= {year_range[1]}"
    
    query += """
        GROUP BY region, year
        HAVING COUNT(DISTINCT country_code) >= 3
        ORDER BY region, year
    """
    
    df = conn.execute(query).df()
    conn.close()
    return df


def get_available_regions():
    """Get list of available regions from the database."""
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    regions = conn.execute("""
        SELECT DISTINCT region 
        FROM indicator_with_region 
        WHERE region != 'Unknown' 
          AND region IS NOT NULL 
          AND region != ''
          AND region != 'Other'
        ORDER BY region
    """).fetchall()
    conn.close()
    return [r[0] for r in regions]


def get_year_range():
    """Get the min and max years from the database."""
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    result = conn.execute("""
        SELECT MIN(year), MAX(year) 
        FROM indicator_with_region
    """).fetchone()
    conn.close()
    return result[0], result[1]


def get_summary_stats(selected_regions=None):
    """Get summary statistics by region."""
    conn = duckdb.connect(str(DB_PATH), read_only=True)
    
    query = """
        SELECT
            region,
            MIN(year) AS first_year,
            MAX(year) AS last_year,
            ROUND(AVG(value), 1) AS avg_rate,
            COUNT(*) AS data_points
        FROM indicator_with_region
        WHERE region != 'Unknown' AND region IS NOT NULL AND region != ''
    """
    
    if selected_regions:
        regions_str = ", ".join([f"'{r}'" for r in selected_regions])
        query += f" AND region IN ({regions_str})"
    
    query += """
        GROUP BY region
        ORDER BY avg_rate DESC
    """
    
    df = conn.execute(query).df()
    conn.close()
    return df


def create_chart(df):
    """Create an Altair line chart."""
    # Configure Altair to handle large datasets
    alt.data_transformers.disable_max_rows()
    
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('year:Q', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('avg_participation_rate:Q', 
                title='Average Participation Rate (%)',
                scale=alt.Scale(zero=False)),
        color=alt.Color('region:N', title='Region'),
        tooltip=[
            alt.Tooltip('region:N', title='Region'),
            alt.Tooltip('year:Q', title='Year', format='d'),
            alt.Tooltip('avg_participation_rate:Q', title='Avg Rate', format='.1f'),
            alt.Tooltip('num_countries:Q', title='Countries')
        ]
    ).properties(
        height=500,
        title='Labor Force Participation Rate by Region Over Time'
    ).interactive()
    
    return chart


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="World Bank Labor Force Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 World Bank Labor Force Analysis")
    st.markdown("""
    This dashboard shows labor force participation rates by region over time,
    using data from the World Bank.
    """)
    
    # Check if database exists
    if not check_database_exists():
        st.error("⚠️ Database not found! Please run `python load_data.py` first to download and prepare the data.")
        st.code("python load_data.py", language="bash")
        return
    
    # Sidebar filters
    st.sidebar.header("🔧 Filters")
    
    # Region filter
    available_regions = get_available_regions()
    selected_regions = st.sidebar.multiselect(
        "Select Regions",
        options=available_regions,
        default=available_regions,
        help="Choose which regions to display"
    )
    
    # Year range filter
    min_year, max_year = get_year_range()
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=int(min_year),
        max_value=int(max_year),
        value=(int(min_year), int(max_year)),
        help="Filter data by year range"
    )
    
    # Get filtered data
    if not selected_regions:
        st.warning("Please select at least one region.")
        return
    
    regional_df = get_regional_data(selected_regions, year_range)
    
    if regional_df.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Main chart
    st.subheader("Labor Force Participation Trends")
    chart = create_chart(regional_df)
    st.altair_chart(chart, width='stretch')
    
    # Summary statistics
    st.subheader("📈 Summary Statistics")
    summary_df = get_summary_stats(selected_regions)
    
    # Display metrics in columns
    cols = st.columns(len(selected_regions) if len(selected_regions) <= 4 else 4)
    for i, (_, row) in enumerate(summary_df.iterrows()):
        col_idx = i % len(cols)
        with cols[col_idx]:
            st.metric(
                label=row['region'],
                value=f"{row['avg_rate']:.1f}%",
                help=f"Data from {int(row['first_year'])} to {int(row['last_year'])}"
            )
    
    # Data table
    with st.expander("📋 View Summary Table"):
        st.dataframe(
            summary_df.rename(columns={
                'region': 'Region',
                'first_year': 'First Year',
                'last_year': 'Last Year',
                'avg_rate': 'Avg Rate (%)',
                'data_points': 'Data Points'
            }),
            width='stretch',
            hide_index=True
        )
    
    # Raw data
    with st.expander("📊 View Raw Data"):
        st.dataframe(
            regional_df.rename(columns={
                'region': 'Region',
                'year': 'Year',
                'avg_participation_rate': 'Avg Participation Rate (%)',
                'num_countries': 'Number of Countries'
            }),
            width='stretch',
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Source:** [World Bank - Labor force participation rate, total](https://data360.worldbank.org/en/indicator/WB_WDI_SL_TLF_CACT_ZS)
    
    **Indicator:** Labor force participation rate, total (% of total population ages 15+)
    """)


if __name__ == "__main__":
    main()