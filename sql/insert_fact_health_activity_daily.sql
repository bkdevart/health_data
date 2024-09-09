-- CREATE OR REPLACE VIEW fact_health_activity_daily AS
INSERT INTO fact_health_activity_daily 
    (customer_id, 
    activity_type_id, 
    source_name,
    start_date, 
    duration_seconds,
    unit, 
    unit_daily_total)
SELECT customer_id, 
    activity_type_id, 
    source_name,
    Date(start_date) AS start_date, 
    SUM(duration_seconds) AS duration_seconds,
    unit, 
    SUM(value) AS unit_daily_total
FROM fact_health_activity_base
WHERE customer_id = '{{ ti.xcom_pull(task_ids='pull_customer_id', key='customer_id') }}'
GROUP BY customer_id, activity_type_id, DATE(start_date), unit, source_name;
