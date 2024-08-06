CREATE TABLE IF NOT EXISTS exercise_time (
    id SERIAL PRIMARY KEY,
    date DATE,
    exercise_time_type VARCHAR,
    exercise_time_duration FLOAT,
    exercise_time_durationUnit VARCHAR,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);