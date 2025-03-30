select 
    borough,
    station_complex,
    latitude,
    longitude,
    count(*) rider_count
from {{ ref('raw_subway_data') }}
group by 
    borough,
    station_complex,
    latitude,
    longitude