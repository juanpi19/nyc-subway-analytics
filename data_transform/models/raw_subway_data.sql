{{ config(materialized='view') }}

SELECT
  transit_timestamp AS ride_date,
  --transit_timestamp::DATE AS ride_date,
  transit_mode,
  station_complex_id,
  station_complex,
  borough,
  payment_method,
  fare_class_category,
  CAST(ridership AS INTEGER) AS ridership,
  CAST(transfers AS INTEGER) AS transfers,
  latitude,
  longitude
FROM {{ source('subway_data', 'mta_subway_complete_2024') }}