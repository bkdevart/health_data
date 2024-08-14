CREATE TABLE IF NOT EXISTS cycling (
    id SERIAL PRIMARY KEY,
    start_date DATE,
    miles FLOAT,
    seconds FLOAT,
    avg_mph FLOAT,
    activity_type_id UUID,
    customer_id UUID
);