CREATE TABLE IF NOT EXISTS combined_data (
    id SERIAL PRIMARY KEY,
    start_date DATE, 
    beats_per_min FLOAT, 
    walking_running_miles FLOAT,
    cycling_miles FLOAT, 
    cycling_seconds FLOAT, 
    cycling_avg_mph FLOAT
);