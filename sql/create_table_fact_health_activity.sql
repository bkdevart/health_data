CREATE TABLE IF NOT EXISTS fact_health_activity (
    activity_id SERIAL PRIMARY KEY,
    customer_id VARCHAR,
    activity_type_id VARCHAR,
    start_date DATE,
    miles FLOAT,
    seconds FLOAT,
    avg_mph FLOAT
);