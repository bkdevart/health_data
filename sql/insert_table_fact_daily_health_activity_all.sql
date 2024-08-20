CREATE TABLE fact_daily_health_activity_all (
    daily_activity_all_id SERIAL PRIMARY KEY,
    customer_id UUID,
    start_date DATE,
    activity_name VARCHAR,
    value FLOAT,
    FOREIGN KEY (customer_id) REFERENCES dim_customer (customer_id)
    );

INSERT INTO fact_daily_health_activity_all
    (customer_id,
    start_date,
    activity_name,
    value)
SELECT 
    customer_id,
    start_date,
    activity_name,
    value
FROM 
    fact_health_activity
LEFT JOIN 
    dim_activity_type USING (activity_type_id)
WHERE 
    activity_name IN (
        'HKQuantityTypeIdentifierHeartRate',
        'HKQuantityTypeIdentifierDistanceCycling',
        'HKQuantityTypeIdentifierDistanceWalkingRunning',
        'HKQuantityTypeIdentifierStepCount',
        'HKQuantityTypeIdentifierBasalEnergyBurned'
    );
