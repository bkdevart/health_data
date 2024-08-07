CREATE TABLE IF NOT EXISTS combined_activity_exercise (
    id SERIAL PRIMARY KEY,
    date DATE,
    energy_burned FLOAT,
    energy_burned_goal INT,
    energy_burned_unit VARCHAR,
    exercise_time INT,
    exercise_time_goal INT,
    stand_hours INT,
    stand_hours_goal INT,
    -- exercise_time_type VARCHAR,
    -- exercise_time_duration FLOAT,
    -- exercise_time_durationUnit VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);