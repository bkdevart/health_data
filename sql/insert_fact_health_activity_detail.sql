CREATE OR REPLACE VIEW fact_health_activity_detail AS
-- INSERT INTO fact_health_activity_detail
    -- (customer_id,
    -- start_date,
    -- activity_name,
    -- source_name,
    -- value,
    -- duration_seconds)
SELECT 
    customer_id,
    start_date,
    activity_name,
    source_name,
    value,
    duration_seconds
FROM 
    fact_health_activity_base
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
