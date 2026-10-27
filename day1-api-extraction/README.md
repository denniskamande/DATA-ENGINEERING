# Day 1: API Data Extraction and Transformation

A Data Engineering project that extracts user data from a REST API, inspects JSON structures, transforms nested records into a tabular format using Python and Pandas, and exports the cleaned data to CSV.

## Tech Stack
- Python
- Requests
- Pandas
- REST API (JSONPlaceholder)

## Pipeline
1. Extract user data from the API.
2. Inspect JSON structure and data types.
3. Extract core customer fields.
4. Flatten nested JSON records.
5. Transform data into a Pandas DataFrame.
6. Export the cleaned data to CSV.

## Output
`output/customers_clean.csv`

## Run Locally
```bash
python -m pip install pandas requests
python extract_customers.py
```

**Learning objectives:** API integration, JSON handling, data transformation, Python data structures, and basic ETL pipeline development.
