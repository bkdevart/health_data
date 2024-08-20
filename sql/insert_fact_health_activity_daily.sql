INSERT INTO fact_health_activity_daily 
    (customer_id, 
    activity_type_id, 
    start_date, 
    duration_seconds,
    unit, 
    unit_daily_total)
SELECT customer_id, 
    activity_type_id, 
    Date(start_date), 
    SUM(duration_seconds) AS duration_seconds,
    unit, 
    SUM(value) AS unit_daily_total
FROM fact_health_activity_base
GROUP BY customer_id, activity_type_id, DATE(start_date), unit;
