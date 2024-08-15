CREATE TABLE IF NOT EXISTS fact_daily_health_activity (
    daily_activity_id SERIAL PRIMARY KEY,
    customer_id UUID,
    activity_name VARCHAR,
    start_date DATE,
    unit VARCHAR,
    daily_total FLOAT,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
);
