INSERT INTO fact_health_activity_summary 
    (customer_id,
    start_date,
    avg_bpm,
    cycling_miles,
    cycling_seconds,
    walking_running_miles,
    walking_running_seconds,
    steps_total,
    step_seconds,
    basal_energy_burned,
    basal_energy_seconds)
SELECT 
    heart_rate.customer_id,
    heart_rate.start_date,
    heart_rate.avg_bpm,
    cycling.cycling_miles,
    cycling.cycling_seconds,
    walk_run.walking_running_miles,
    walk_run.walking_running_seconds,
    steps.steps_total,
    steps.step_seconds,
    basal.basal_energy_burned,
    basal.basal_energy_seconds
FROM 
    (SELECT customer_id, DATE(start_date) AS start_date,
         AVG(value) AS avg_bpm
     FROM fact_health_activity_base
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierHeartRate'
     GROUP BY customer_id, DATE(start_date)) heart_rate
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS cycling_miles, duration_seconds AS cycling_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceCycling') cycling
ON heart_rate.customer_id = cycling.customer_id AND heart_rate.start_date = cycling.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS walking_running_miles, duration_seconds AS walking_running_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceWalkingRunning') walk_run
ON heart_rate.customer_id = walk_run.customer_id AND heart_rate.start_date = walk_run.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS steps_total, duration_seconds AS step_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierStepCount') steps
ON heart_rate.customer_id = steps.customer_id AND heart_rate.start_date = steps.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS basal_energy_burned, duration_seconds AS basal_energy_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierBasalEnergyBurned') basal
ON heart_rate.customer_id = basal.customer_id AND heart_rate.start_date = basal.start_date;
