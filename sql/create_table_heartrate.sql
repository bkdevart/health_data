CREATE TABLE IF NOT EXISTS heartrate (
    id SERIAL PRIMARY KEY,
    start_date DATE,
    beats_per_min FLOAT
);