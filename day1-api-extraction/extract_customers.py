
"""
Day 1 - API Data Extraction and Transformation
Squad Python Specialization - Data Engineering

Extract users from an API, inspect the JSON structure,
transform nested records into a flat DataFrame, and export to CSV.
"""

from pathlib import Path

import pandas as pd
import requests
import csv
import json
import sys

API_URL = "https://jsonplaceholder.typicode.com/users"
OUTPUT_PATH = Path("output") / "customers_clean.csv"

EXPECTED_COLUMNS = [
    "customer_id",
    "name",
    "username",
    "email",
    "phone",
    "website",
    "address_street",
    "address_suite",
    "address_city",
    "address_zipcode",
    "address_geo_lat",
    "address_geo_lng",
    "company_name",
    "company_catchphrase",
    "company_bs",
]


def fetch_users(
    url: str = API_URL,
    timeout: float = 10.0,
) -> list[dict]:
    """Retrieve and validate user records from the API."""

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        payload = response.json()

    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"API request timed out after {timeout} seconds."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise RuntimeError(
            "Failed to connect to the API. Check your internet connection or URL."
        ) from exc

    except requests.exceptions.HTTPError as exc:
        raise RuntimeError(
            f"API returned an unsuccessful HTTP status: {exc}"
        ) from exc

    except requests.exceptions.JSONDecodeError as exc:
        raise RuntimeError(
            "The API response is not valid JSON."
        ) from exc

    if not isinstance(payload, list):
        raise ValueError("Expected the API response to be a list.")

    if not all(isinstance(user, dict) for user in payload):
        raise ValueError(
            "Invalid API response: every user record must be a dictionary."
        )

    return payload


def describe_structure(payload: list[dict]) -> None:
    """Print the payload type, record type, and nested field types."""

    print("----------Data Structure Description-------------")
    print(f"Payload type: {type(payload).__name__}")

    if not payload:
        print("Payload is an empty list.")
        print()
        return

    record = payload[0]
    print(f"Record type: {type(record).__name__}")
    print("Nested fields in a record:")

    for key, value in record.items():
        if isinstance(value, dict):
            print(f" - {key}: dict(depth 1)")

            for nested_key, nested_value in value.items():
                if isinstance(nested_value, dict):
                    print(f"    - {nested_key}: dict(depth 2)")

                    for inner_key, inner_value in nested_value.items():
                        print(
                            f"        - {inner_key}: "
                            f"{type(inner_value).__name__}"
                        )
                else:
                    print(
                        f"    - {nested_key}: "
                        f"{type(nested_value).__name__}"
                    )
        else:
            print(f" - {key}: {type(value).__name__}")

    print()


def extract_core_fields(users: list[dict]) -> list[dict]:
    """Extract ID, name, email, city, and company name for each user."""

    extracted = []

    for user in users:
        address = user.get("address") or {}
        company = user.get("company") or {}

        extracted.append(
            {
                "id": user.get("id"),
                "name": user.get("name"),
                "email": user.get("email"),
                "city": address.get("city", "Unknown"),
                "company": company.get("name", "Unknown"),
            }
        )

    return extracted


def build_structures(
    users: list[dict],
) -> tuple[list, list[tuple], dict]:
    """
    Return names, (ID, email) tuples, and an ID-to-city dictionary.

    Demonstrates list and dictionary comprehensions.
    """

    names = [user.get("name") for user in users]

    id_email_tuples = [
        (user.get("id"), user.get("email"))
        for user in users
    ]

    id_to_city = {
        user.get("id"): (user.get("address") or {}).get(
            "city", "Unknown"
        )
        for user in users
    }

    return names, id_email_tuples, id_to_city


def flatten_user(
    user: dict,
    parent_key: str = "",
    sep: str = "_",
) -> dict:
    """Recursively flatten nested dictionaries into a single dictionary."""

    items = []

    for key, value in user.items():
        key = key.lower()
        new_key = f"{parent_key}{sep}{key}" if parent_key else key

        if isinstance(value, dict):
            items.extend(
                flatten_user(value, new_key, sep=sep).items()
            )
        else:
            items.append((new_key, value))

    return dict(items)


def to_dataframe(flat_users: list[dict]) -> pd.DataFrame:
    """Create a DataFrame with consistent column names and ordering."""

    df = pd.DataFrame(flat_users)

    if "id" in df.columns:
        df = df.rename(columns={"id": "customer_id"})

    # Ensure coordinates are numeric when present.
    for column in ("address_geo_lat", "address_geo_lng"):
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

    # Guarantee the expected columns and their order.
    # Missing fields are filled with pandas missing values.
    df = df.reindex(columns=EXPECTED_COLUMNS)

    return df


def export_csv(
    df: pd.DataFrame,
    path: Path = OUTPUT_PATH,
) -> Path:
    """Create the output directory, export the CSV, and return its path."""

    path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(path, index=False, encoding="utf-8")

    return path


def main() -> None:
    """Run the complete API extraction and transformation pipeline."""

    print("Starting API data extraction...")
    print(f"Fetching data from {API_URL}...")

    try:
        users = fetch_users()
    except (RuntimeError, ValueError) as exc:
        print(f"Extraction failed: {exc}")
        return

    print(f"Fetched data successfully. Fetched {len(users)} records.")
    print()

    # Inspect the JSON structure.
    describe_structure(users)

    # Extract core fields.
    core_fields = extract_core_fields(users)

    print("----------Core Fields----------------")
    print(f"{len(core_fields)} users extracted.")

    for user in core_fields[:5]:
        print(user)

    print()

    # Demonstrate Python data structures.
    names, tuples, city_dict = build_structures(users)

    print("-------Structuring Data Demo-----------")
    print(f"First 5 names: {names[:5]}")
    print(f"First 5 (id, email) tuples: {tuples[:5]}")
    print(f"ID -> City mapping: {list(city_dict.items())[:5]}")
    print()

    # Flatten the nested JSON records.
    flat_users = [flatten_user(user) for user in users]

    print("-----------Flattened Users---------------")
    print(f"{len(flat_users)} records flattened.")
    print()

    # Convert to a DataFrame.
    df = to_dataframe(flat_users)

    print("---------DataFrame Info-------------")
    print(f"Shape: {df.shape}")
    print("Data Types:")
    print(df.dtypes)
    print()

    # Export the transformed dataset.
    try:
        saved_data_path = export_csv(df)
    except (OSError, ValueError) as exc:
        print(f"CSV export failed: {exc}")
        return

    print(f"Cleaned data exported to: {saved_data_path}")
    print()
    print("----------Run Summary----------------")
    print(f"Records extracted: {len(users)}")
    print(f"Records transformed: {len(df)}")
    print(f"Columns exported: {len(df.columns)}")
    print(f"Output file: {saved_data_path}")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
