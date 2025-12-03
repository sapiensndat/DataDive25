#!/usr/bin/env python3
"""
World Bank Labor Force Data Loader

This script downloads World Bank labor force participation data and loads it
into a DuckDB database for analysis.

Usage:
    python load_data.py

This will create:
    - data/labor_force_data.csv - Raw indicator data
    - data/data_dictionary.csv - Metadata about countries
    - data/worldbank.duckdb - DuckDB database with cleaned tables
"""

import requests
import duckdb
from pathlib import Path


# Configuration
DATA_DIR = Path(__file__).parent / "data"
INDICATOR_URL = "https://data360files.worldbank.org/data360-data/data/WB_WDI/WB_WDI_SL_TLF_CACT_ZS.csv"
DICTIONARY_URL = "https://data360files.worldbank.org/data360-data/data/WB_WDI/WB_WDI_SL_TLF_CACT_ZS_DATADICT.csv"
INDICATOR_FILE = DATA_DIR / "labor_force_data.csv"
DICTIONARY_FILE = DATA_DIR / "data_dictionary.csv"
DB_PATH = DATA_DIR / "worldbank.duckdb"


def download_data():
    """Download World Bank data files if they don't exist."""
    DATA_DIR.mkdir(exist_ok=True)
    
    # Download indicator data
    if not INDICATOR_FILE.exists():
        print("Downloading indicator data...")
        response = requests.get(INDICATOR_URL, timeout=60)
        response.raise_for_status()
        INDICATOR_FILE.write_bytes(response.content)
        print(f"Saved to {INDICATOR_FILE}")
    else:
        print(f"Using cached file: {INDICATOR_FILE}")
    
    # Download dictionary data
    if not DICTIONARY_FILE.exists():
        print("Downloading dictionary data...")
        response = requests.get(DICTIONARY_URL, timeout=60)
        response.raise_for_status()
        DICTIONARY_FILE.write_bytes(response.content)
        print(f"Saved to {DICTIONARY_FILE}")
    else:
        print(f"Using cached file: {DICTIONARY_FILE}")


def load_into_duckdb():
    """Load CSV data into DuckDB and create cleaned tables."""
    print(f"\nConnecting to DuckDB: {DB_PATH}")
    conn = duckdb.connect(str(DB_PATH))
    
    # Load indicator CSV directly into DuckDB
    print("Loading indicator data...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE indicator_raw AS
        SELECT * FROM read_csv_auto('{INDICATOR_FILE}', header=True)
    """)
    row_count = conn.execute("SELECT COUNT(*) FROM indicator_raw").fetchone()[0]
    print(f"Loaded indicator_raw: {row_count:,} rows")
    
    # Load dictionary CSV directly into DuckDB
    print("Loading dictionary data...")
    conn.execute(f"""
        CREATE OR REPLACE TABLE dictionary AS
        SELECT DISTINCT * FROM read_csv_auto('{DICTIONARY_FILE}', header=True)
    """)
    row_count = conn.execute("SELECT COUNT(*) FROM dictionary").fetchone()[0]
    print(f"Loaded dictionary: {row_count:,} rows")
    
    # Create cleaned indicator table
    print("Creating cleaned indicator table...")
    conn.execute("""
        CREATE OR REPLACE TABLE indicator_clean AS
        SELECT
            REF_AREA AS country_code,
            REF_AREA_LABEL AS country_name,
            CAST(TIME_PERIOD AS INTEGER) AS year,
            CAST(OBS_VALUE AS DOUBLE) AS value,
            INDICATOR_LABEL AS indicator_name
        FROM indicator_raw
        WHERE OBS_VALUE IS NOT NULL
          AND TIME_PERIOD IS NOT NULL
    """)
    row_count = conn.execute("SELECT COUNT(*) FROM indicator_clean").fetchone()[0]
    print(f"Created indicator_clean: {row_count:,} rows")
    
    # Create region mapping table
    print("Creating region mapping table...")
    conn.execute("""
        CREATE OR REPLACE TABLE region_mapping AS
        SELECT * FROM (VALUES
            -- East Asia & Pacific
            ('CHN', 'East Asia & Pacific'),
            ('JPN', 'East Asia & Pacific'),
            ('KOR', 'East Asia & Pacific'),
            ('AUS', 'East Asia & Pacific'),
            ('IDN', 'East Asia & Pacific'),
            ('THA', 'East Asia & Pacific'),
            ('VNM', 'East Asia & Pacific'),
            ('MYS', 'East Asia & Pacific'),
            ('PHL', 'East Asia & Pacific'),
            ('NZL', 'East Asia & Pacific'),
            -- Europe & Central Asia
            ('DEU', 'Europe & Central Asia'),
            ('FRA', 'Europe & Central Asia'),
            ('GBR', 'Europe & Central Asia'),
            ('ITA', 'Europe & Central Asia'),
            ('ESP', 'Europe & Central Asia'),
            ('POL', 'Europe & Central Asia'),
            ('NLD', 'Europe & Central Asia'),
            ('TUR', 'Europe & Central Asia'),
            ('RUS', 'Europe & Central Asia'),
            ('UKR', 'Europe & Central Asia'),
            -- Latin America & Caribbean
            ('BRA', 'Latin America & Caribbean'),
            ('MEX', 'Latin America & Caribbean'),
            ('ARG', 'Latin America & Caribbean'),
            ('COL', 'Latin America & Caribbean'),
            ('CHL', 'Latin America & Caribbean'),
            ('PER', 'Latin America & Caribbean'),
            ('VEN', 'Latin America & Caribbean'),
            -- Middle East & North Africa
            ('EGY', 'Middle East & North Africa'),
            ('SAU', 'Middle East & North Africa'),
            ('IRN', 'Middle East & North Africa'),
            ('IRQ', 'Middle East & North Africa'),
            ('MAR', 'Middle East & North Africa'),
            ('DZA', 'Middle East & North Africa'),
            -- North America
            ('USA', 'North America'),
            ('CAN', 'North America'),
            -- South Asia
            ('IND', 'South Asia'),
            ('PAK', 'South Asia'),
            ('BGD', 'South Asia'),
            ('LKA', 'South Asia'),
            ('NPL', 'South Asia'),
            -- Sub-Saharan Africa
            ('NGA', 'Sub-Saharan Africa'),
            ('ZAF', 'Sub-Saharan Africa'),
            ('KEN', 'Sub-Saharan Africa'),
            ('ETH', 'Sub-Saharan Africa'),
            ('GHA', 'Sub-Saharan Africa'),
            ('TZA', 'Sub-Saharan Africa')
        ) AS t(country_code, region)
    """)
    print("Created region_mapping table")
    
    # Join with region mapping to add region information
    print("Creating indicator_with_region table...")
    conn.execute("""
        CREATE OR REPLACE TABLE indicator_with_region AS
        SELECT
            i.*,
            COALESCE(r.region, 'Other') AS region
        FROM indicator_clean i
        LEFT JOIN region_mapping r ON UPPER(i.country_code) = r.country_code
    """)
    row_count = conn.execute("SELECT COUNT(*) FROM indicator_with_region").fetchone()[0]
    print(f"Created indicator_with_region: {row_count:,} rows")
    
    conn.close()
    print("\nDatabase setup complete!")


def main():
    """Main entry point."""
    print("=" * 60)
    print("World Bank Labor Force Data Loader")
    print("=" * 60)
    
    download_data()
    load_into_duckdb()
    
    print("\n" + "=" * 60)
    print("Data loading complete!")
    print(f"Database saved to: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()