CREATE TABLE IF NOT EXISTS combined_data (
    id SERIAL PRIMARY KEY,
    start_date DATE, 
    beats_per_min FLOAT, 
    walking_running_miles FLOAT,
    cycling_miles FLOAT, 
    cycling_seconds FLOAT, 
    cycling_avg_mph FLOAT,
    energy_burned FLOAT,
    energy_burned_goal INT,
    energy_burned_unit VARCHAR,
    exercise_time INT,
    exercise_time_goal INT,
    stand_hours INT,
    stand_hours_goal INT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);