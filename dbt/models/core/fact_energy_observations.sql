{{ config(materialized='table') }}

with staging as (
    select * from {{ ref('stg_eurostat') }}
)

select
    -- Generate a unique surrogate key for each observation
    {{ dbt_utils.generate_surrogate_key(['dataset_code', 'geo', 'indicator', 'observation_date']) }} as observation_key,
    dataset_code,
    geo as country_code,
    country_name,
    indicator as indicator_code,
    indicator_label,
    unit_code,
    unit_label,
    observation_date as time,
    observation_year as year,
    energy_value as value,
    load_timestamp,
    CURRENT_TIMESTAMP as dbt_transformed_at
from staging
