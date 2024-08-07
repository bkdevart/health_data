-- TODO: join in other datasets
INSERT INTO combined_activity_exercise 
    (date, 
    energy_burned, 
    energy_burned_goal,
    energy_burned_unit, 
    exercise_time, 
    exercise_time_goal,
    stand_hours,
    stand_hours_goal,
    created_at,
    updated_at)
SELECT date, 
    energy_burned, 
    energy_burned_goal,
    energy_burned_unit,
    exercise_time,
    exercise_time_goal,
    stand_hours,
    stand_hours_goal,
    created_at,
    updated_at

FROM activity_summary;
-- LEFT JOIN (
--     SELECT 
--         date, 
--         exercise_time_type,
--         exercise_time_durationUnit,
--         SUM(exercise_time_duration) AS summed_exercise_time_duration
--     FROM 
--         exercise_time
--     GROUP BY 
--         date, 
--         exercise_time_type,
--         exercise_time_durationUnit
-- ) AS exercise_time
-- USING (date);