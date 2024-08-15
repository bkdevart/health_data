CREATE TABLE IF NOT EXISTS fact_daily_health_activity (
    daily_activity_id SERIAL PRIMARY KEY,
    customer_id UUID,
    activity_type_id UUID,
    start_date DATE,
    duration_seconds INT,
    unit VARCHAR,
    unit_daily_total FLOAT,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    FOREIGN KEY (activity_type_id) REFERENCES dim_activity_type (activity_type_id)
);
