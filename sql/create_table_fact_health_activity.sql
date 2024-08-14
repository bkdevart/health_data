CREATE TABLE IF NOT EXISTS fact_health_activity (
    activity_id SERIAL PRIMARY KEY,
    customer_id UUID,
    activity_type_id UUID,
    start_date DATE,
    source_name VARCHAR,
    unit VARCHAR,
    value FLOAT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    FOREIGN KEY (activity_type_id) REFERENCES dim_activity_type (activity_type_id)
);

-- SELECT customer_id, activity_name, start_date, unit, SUM(value)
-- FROM fact_health_activity
-- LEFT JOIN dim_activity_type USING (activity_type_id)
-- GROUP BY customer_id, activity_name, start_date, unit
-- LIMIT 5;