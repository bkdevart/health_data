INSERT INTO fact_daily_health_activity (customer_id, activity_type_id, start_date, unit, daily_total)
SELECT customer_id, activity_type_id, start_date, unit, SUM(value) AS daily_total
FROM fact_health_activity
GROUP BY customer_id, activity_type_id, start_date, unit;
