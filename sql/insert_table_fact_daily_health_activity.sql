INSERT INTO fact_daily_health_activity (customer_id, activity_name, start_date, unit, daily_total)
SELECT customer_id, activity_name, start_date, unit, SUM(value) AS daily_total
FROM fact_health_activity
LEFT JOIN dim_activity_type USING (activity_type_id)
GROUP BY customer_id, activity_name, start_date, unit;
