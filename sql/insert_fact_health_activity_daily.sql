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


-- check
SELECT customer_id, 
    activity_type_id, 
    Date(start_date), 
    SUM(duration_seconds) AS duration_seconds,
    unit, 
    SUM(value) AS unit_daily_total
FROM fact_health_activity_base
WHERE customer_id = '3d439eab-be08-4944-a64c-4ba4e82ffd10' 
    AND activity_type_id = 'ce0c37ce-84b9-4be0-a2cf-561efdae976b' 
    AND DATE(start_date) = '2024-07-02'
GROUP BY customer_id, activity_type_id, DATE(start_date), unit;