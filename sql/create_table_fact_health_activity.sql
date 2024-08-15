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