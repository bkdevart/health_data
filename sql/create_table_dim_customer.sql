CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birthday DATE,
    sex VARCHAR(30),
    blood_type VARCHAR(30)
);