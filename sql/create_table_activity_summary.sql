CREATE TABLE IF NOT EXISTS activity_summary (
    id SERIAL PRIMARY KEY,
    date DATE,
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