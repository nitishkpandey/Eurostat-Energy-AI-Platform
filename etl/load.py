import time
import psycopg2
from sqlalchemy import create_engine, text, Engine
import pandas as pd
from .config import DB_NAME, DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_URL

def wait_for_db(max_retries=20, delay=5):
    """
    Waits for the database to become available.
    """
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.close()
            print("PostgreSQL is available.")
            return
        except psycopg2.OperationalError:
            print(f"Waiting for PostgreSQL... attempt {i + 1}")
            time.sleep(delay)
    raise Exception("Could not connect to PostgreSQL after multiple attempts.")

def get_engine() -> Engine:
    """Returns the SQLAlchemy engine."""
    return create_engine(DB_URL)

def init_db(engine: Engine, mode: str):
    """
    Initializes the database table based on the mode.
    modes: 'full-refresh', 'truncate', 'append'
    """
    create_table_sql = """
            CREATE TABLE IF NOT EXISTS observations (
                id SERIAL PRIMARY KEY,
                dataset_code TEXT,
                country_code TEXT,
                country_name TEXT,
                indicator_code TEXT,
                indicator_label TEXT,
                unit_code TEXT,
                unit_label TEXT,
                time DATE,
                value FLOAT,
                load_timestamp TIMESTAMP
            );
    """
    
    with engine.begin() as conn:
        if mode == "full-refresh":
            conn.execute(text("DROP TABLE IF EXISTS observations"))
            conn.execute(text(create_table_sql))
            print("Dropped and recreated 'observations' table.")
        elif mode == "truncate":
            conn.execute(text("TRUNCATE TABLE observations"))
            print("Truncated 'observations' table.")
        elif mode == "append":
            conn.execute(text(create_table_sql))
            print("Append mode: ensured 'observations' table exists.")

def load_data_to_db(df: pd.DataFrame, engine: Engine):
    """
    Loads the DataFrame into the database.
    """
    if df.empty:
        print("No data to load.")
        return
        
    df.to_sql("observations", engine, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows to 'observations' table.")
