INSERT INTO combined_data (start_date, beats_per_min, walking_running_miles,
    cycling_miles, cycling_seconds, cycling_avg_mph)
SELECT heartrate.start_date, 
    beats_per_min, 
    walking_running.miles AS walking_running_miles,
    cycling.miles AS cycling_miles,
    cycling.seconds AS cycling_seconds,
    cycling.avg_mph AS cycling_avg_mph
FROM heartrate
LEFT JOIN walking_running
USING (start_date)
LEFT JOIN cycling
USING (start_date);