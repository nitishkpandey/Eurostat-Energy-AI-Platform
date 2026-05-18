import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.providers.dbt.cloud.operators.dbt import DbtCloudRunJobOperator

# Import our existing Python ETL logic to run inside Airflow
# (In a real production environment, you would package the backend as a module)
# from backend.etl.main import main as run_python_etl

default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'eurostat_energy_pipeline',
    default_args=default_args,
    description='Extract Eurostat Energy Data, Load to Postgres, and Transform with dbt',
    schedule_interval='@daily',
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['eurostat', 'energy', 'dbt'],
) as dag:

    # Task 1: Wait for database to be ready (Sensor or Bash check)
    check_db_ready = BashOperator(
        task_id='check_db_ready',
        bash_command='pg_isready -h postgres -p 5432 -U eurostat_admin'
    )

    # Task 2: Extract & Load Raw Data
    # In a modern ELT stack, we just dump the raw JSON from the API straight into the DB.
    # For now, we wrap our existing Python script.
    extract_and_load = BashOperator(
        task_id='extract_raw_eurostat_data',
        bash_command='cd /opt/airflow/app && uv run python -m backend.etl.main',
        # Alternately: PythonOperator(task_id='run_etl', python_callable=run_python_etl)
    )

    # Task 3: Transform Data using dbt (Data Build Tool)
    # This turns the raw JSON/CSV into a clean Star Schema / Fact Table using SQL in Postgres
    run_dbt_transform = BashOperator(
        task_id='dbt_run_models',
        bash_command='cd /opt/airflow/app/dbt && dbt run --profiles-dir .',
    )
    
    # Task 4: Generate dbt Documentation
    generate_dbt_docs = BashOperator(
        task_id='dbt_generate_docs',
        bash_command='cd /opt/airflow/app/dbt && dbt docs generate --profiles-dir .',
    )

    # Define the execution graph (Dependencies)
    check_db_ready >> extract_and_load >> run_dbt_transform >> generate_dbt_docs
