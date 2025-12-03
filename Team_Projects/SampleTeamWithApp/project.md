# Labor Force Analytics Team

This is a sample team project that demonstrates how to build an interactive Streamlit dashboard for analyzing labor force statistics.

## Overview

Team Labor Force Analytics developed an interactive Streamlit application to explore and visualize labor force participation trends across demographics, regions, and time periods. Using data from the Bureau of Labor Statistics (BLS) and International Labour Organization (ILO), we identified key patterns in workforce participation rates, unemployment trends, and the impact of economic events on employment. Our analysis reveals significant disparities in labor force participation across age groups and genders, with particular emphasis on post-pandemic recovery patterns.

## Team Members

- Marcus Chen
- Sarah Williams
- Diego Rodriguez
- Aisha Patel
- Jordan Thompson

## Challenge Category Area

See https://www.dc2.org/datadive for details on the challenge areas. Specify which challenge category your team is addressing.

Category 2: Labor Markets and Workforce Development

## Project Description

Team Labor Force Analytics built an interactive Streamlit dashboard to analyze and visualize labor force participation data from multiple sources including BLS and ILO datasets. The application enables users to explore employment trends, unemployment rates, and labor force participation across different demographic segments.

Key features of our Streamlit application include:

- **Interactive Time Series Analysis**: Visualize labor force participation rates over time with adjustable date ranges and demographic filters
- **Regional Comparisons**: Compare labor force statistics across countries, states, or metropolitan areas using choropleth maps and bar charts
- **Demographic Breakdowns**: Analyze participation rates by age group, gender, education level, and industry sector
- **Economic Indicator Correlations**: Explore relationships between labor force metrics and economic indicators like GDP growth and inflation
- **Forecasting Module**: Machine learning-based predictions for future labor force trends using historical patterns

The dashboard is built with Streamlit for the frontend, pandas for data manipulation, and Plotly/Altair for interactive visualizations. Data is stored and queried using DuckDB for efficient analysis of large datasets.

Our analysis highlights the uneven recovery in labor force participation post-2020, with younger workers (16-24) showing slower return rates compared to prime-age workers (25-54). The tool helps policymakers and researchers understand these dynamics and identify interventions to improve workforce participation.

## Links:

- [Live Demo](app/streamlit_app.py)
- slides.pdf
- [Data Sources](data/README.md)