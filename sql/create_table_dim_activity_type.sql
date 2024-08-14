CREATE TABLE IF NOT EXISTS dim_activity_type (
    activity_type_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    activity_name VARCHAR
);