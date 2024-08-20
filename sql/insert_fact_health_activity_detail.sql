INSERT INTO fact_health_activity_detail
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
