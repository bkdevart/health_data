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
    COALESCE(cycling.cycling_miles, 0) AS cycling_miles,
    COALESCE(cycling.cycling_seconds, 0) AS cycling_seconds,
    COALESCE(walk_run.walking_running_miles, 0) AS walking_running_miles,
    COALESCE(walk_run.walking_running_seconds, 0) AS walking_running_seconds,
    COALESCE(steps.steps_total, 0) AS steps_total,
    COALESCE(steps.step_seconds, 0) AS step_seconds,
    COALESCE(basal.basal_energy_burned, 0) AS basal_energy_burned,
    COALESCE(basal.basal_energy_seconds, 0) AS basal_energy_seconds
FROM 
    (SELECT customer_id, DATE(start_date) AS start_date,
         AVG(value) AS avg_bpm
     FROM fact_health_activity_base
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierHeartRate'
     GROUP BY customer_id, DATE(start_date)) heart_rate
LEFT JOIN 
    (SELECT customer_id, start_date, 
             SUM(unit_daily_total) AS cycling_miles, 
             SUM(duration_seconds) AS cycling_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceCycling'
     GROUP BY customer_id, start_date) cycling
ON heart_rate.customer_id = cycling.customer_id AND heart_rate.start_date = cycling.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, 
             SUM(unit_daily_total) AS walking_running_miles, 
             SUM(duration_seconds) AS walking_running_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceWalkingRunning'
     GROUP BY customer_id, start_date) walk_run
ON heart_rate.customer_id = walk_run.customer_id AND heart_rate.start_date = walk_run.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, 
             SUM(unit_daily_total) AS steps_total, 
             SUM(duration_seconds) AS step_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierStepCount'
     GROUP BY customer_id, start_date) steps
ON heart_rate.customer_id = steps.customer_id AND heart_rate.start_date = steps.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, 
             SUM(unit_daily_total) AS basal_energy_burned, 
             SUM(duration_seconds) AS basal_energy_seconds
     FROM fact_health_activity_daily
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierBasalEnergyBurned'
     GROUP BY customer_id, start_date) basal
ON heart_rate.customer_id = basal.customer_id AND heart_rate.start_date = basal.start_date;
