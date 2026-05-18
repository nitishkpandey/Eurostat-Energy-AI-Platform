{{ config(materialized='view') }}

with raw_data as (
    -- In a true ELT pipeline, this would point to a raw JSON dump table loaded by Airflow (e.g., raw_eurostat_json)
    -- For demonstration, we assume a raw table `raw_observations` exists.
    select * from {{ source('public', 'raw_observations') }}
)

select
    dataset_code,
    country_code as geo,
    country_name,
    indicator_code as indicator,
    indicator_label,
    unit_code,
    unit_label,
    CAST(time as DATE) as observation_date,
    EXTRACT(YEAR FROM CAST(time as DATE)) as observation_year,
    CAST(value as FLOAT) as energy_value,
    load_timestamp
from raw_data
where value is not null
