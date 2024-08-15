INSERT INTO fact_daily_health_activity 
    (customer_id, 
    activity_type_id, 
    start_date, 
    duration_seconds,
    unit, 
    unit_daily_total)
SELECT customer_id, 
    activity_type_id, 
    Date(start_date), 
    SUM(duration_seconds) AS duration_seconds,
    unit, 
    SUM(value) AS unit_daily_total
FROM fact_health_activity
GROUP BY customer_id, activity_type_id, DATE(start_date), unit;

-- new
SELECT 
    cycling.customer_id,
    cycling.start_date,
    cycling.cycling_miles,
    cycling.cycling_seconds,
    walk_run.walking_running_miles,
    walk_run.walking_running_seconds,
    steps.steps_total,
    steps.step_seconds,
    basal.basal_energy_burned,
    basal.basal_energy_seconds
FROM 
    (SELECT customer_id, start_date, unit_daily_total AS cycling_miles, duration_seconds AS cycling_seconds
     FROM fact_daily_health_activity
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceCycling') cycling
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS walking_running_miles, duration_seconds AS walking_running_seconds
     FROM fact_daily_health_activity
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierDistanceWalkingRunning') walk_run
ON cycling.customer_id = walk_run.customer_id AND cycling.start_date = walk_run.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS steps_total, duration_seconds AS step_seconds
     FROM fact_daily_health_activity
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierStepCount') steps
ON cycling.customer_id = steps.customer_id AND cycling.start_date = steps.start_date
LEFT JOIN 
    (SELECT customer_id, start_date, unit_daily_total AS basal_energy_burned, duration_seconds AS basal_energy_seconds
     FROM fact_daily_health_activity
     LEFT JOIN dim_activity_type USING (activity_type_id)
     WHERE activity_name = 'HKQuantityTypeIdentifierBasalEnergyBurned') basal
ON cycling.customer_id = basal.customer_id AND cycling.start_date = basal.start_date;
