CREATE TABLE IF NOT EXISTS fact_health_activity_summary (
    daily_activity_summary_id SERIAL PRIMARY KEY,
    customer_id UUID,
    start_date DATE,
    source_name VARCHAR,
    avg_bpm FLOAT,
    cycling_miles FLOAT,
    cycling_seconds INT,
    walking_running_miles FLOAT,
    walking_running_seconds INT,
    steps_total INT,
    step_seconds INT,
    basal_energy_burned FLOAT,
    basal_energy_seconds INT,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
);
