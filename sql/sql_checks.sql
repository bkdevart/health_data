-- check specific user, activity_type_id
SELECT *
FROM fact_health_activity_base 
WHERE customer_id = '6327daa0-946e-4c05-930f-f4b445133c88' 
    AND activity_type_id = '4d189e3d-1eec-49ee-836d-97ae15b9ce13' 
    AND DATE(start_date) = '2024-08-20'
LIMIT 5;

-- find out how many source_name values for a given day/period and activity from base data
SELECT source_name, count(*) AS total, sum(value) as miles
FROM fact_health_activity_base 
WHERE customer_id = '6327daa0-946e-4c05-930f-f4b445133c88' 
    AND activity_type_id = '4d189e3d-1eec-49ee-836d-97ae15b9ce13' 
    AND DATE(start_date) = '2024-08-20'
GROUP BY source_name;

-- find out how many source_name values for a given day/period daily data
SELECT count(*) AS total, sum(unit_daily_total) as miles
FROM fact_health_activity_daily
WHERE customer_id = '6327daa0-946e-4c05-930f-f4b445133c88' 
    AND activity_type_id = '4d189e3d-1eec-49ee-836d-97ae15b9ce13' 
    AND DATE(start_date) = '2024-08-20'
GROUP BY start_date;

-- more daily information
SELECT customer_id, 
    activity_type_id, 
    Date(start_date), 
    SUM(duration_seconds) AS duration_seconds,
    unit, 
    SUM(value) AS unit_daily_total
FROM fact_health_activity_base
WHERE customer_id = '6327daa0-946e-4c05-930f-f4b445133c88' 
    -- walking_running
    AND activity_type_id = '4d189e3d-1eec-49ee-836d-97ae15b9ce13' 
    AND DATE(start_date) = '2024-08-20'
GROUP BY customer_id, activity_type_id, DATE(start_date), unit;

-- find out how many source_name values for a given day/period summary data
SELECT count(*) AS total, sum(walking_running_miles) as miles
FROM fact_health_activity_summary
WHERE customer_id = '6327daa0-946e-4c05-930f-f4b445133c88' 
    -- AND activity_type_id = '4d189e3d-1eec-49ee-836d-97ae15b9ce13' 
    AND DATE(start_date) = '2024-08-20'
GROUP BY start_date;
