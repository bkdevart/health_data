CREATE TABLE  IF NOT EXISTS fact_health_activity_detail (
    daily_activity_all_id SERIAL PRIMARY KEY,
    customer_id UUID,
    start_date TIMESTAMP,
    activity_name VARCHAR,
    value FLOAT,
    duration_seconds INT,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
    );
