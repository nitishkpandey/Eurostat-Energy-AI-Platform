import argparse
import pandas as pd
from etl.config import DATASETS
from etl.extract import fetch_dataset
from etl.transform import transform_dataset
from etl.load import wait_for_db, get_engine, init_db, load_data_to_db

def main():
    # --- Command Line Interface (CLI) argument for load mode ---
    parser = argparse.ArgumentParser(description="ETL pipeline mode")
    parser.add_argument("--mode", choices=["append", "truncate", "full-refresh"], default="full-refresh", help="Data load mode")
    args = parser.parse_args()

    # --- 1. Database Setup ---
    wait_for_db()
    engine = get_engine()
    init_db(engine, args.mode)

    # --- 2. Extract & Transform ---
    all_dataframes = []

    for dataset_code, config in DATASETS.items():
        print(f"Processing dataset: {dataset_code}...")
        
        # Extract
        raw_data = fetch_dataset(dataset_code, config["url"])
        if not raw_data:
            continue
            
        # Transform
        df = transform_dataset(dataset_code, raw_data, config["indicators"])
        if not df.empty:
            all_dataframes.append(df)

    # --- 3. Load ---
    if all_dataframes:
        full_df = pd.concat(all_dataframes, ignore_index=True)
        load_data_to_db(full_df, engine)
    else:
        print("No data transformed successfully.")

if __name__ == "__main__":
    main()