select 
    borough,
    extract(dow from strptime(ride_date, '%m/%d/%Y %I:%M:%S %p')::date) as day_of_week,
    count(*) rider_count
from {{ ref('raw_subway_data') }}
group by
    borough,
    extract(dow from strptime(ride_date, '%m/%d/%Y %I:%M:%S %p')::date)

