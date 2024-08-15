CREATE TABLE IF NOT EXISTS fact_health_activity (
    activity_id SERIAL PRIMARY KEY,
    customer_id UUID,
    activity_type_id UUID,
    source_name VARCHAR,
    unit VARCHAR,
    value FLOAT,
    duration_seconds INT,
    start_date TIMESTAMP,
    creation_date TIMESTAMP,
    end_date TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id),
    FOREIGN KEY (activity_type_id) REFERENCES dim_activity_type (activity_type_id)
);