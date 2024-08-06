INSERT INTO combined_activity_exercise 
    (date, 
    energy_burned, 
    energy_burned_goal,
    energy_burned_unit, 
    exercise_time, 
    exercise_time_goal,
    stand_hours,
    stand_hours_goal,
    exercise_time_type,
    exercise_time_duration,
    exercise_time_durationUnit,
    created_at,
    updated_at)
SELECT activity_summary.date, 
    energy_burned, 
    energy_burned_goal,
    energy_burned_unit,
    exercise_time,
    exercise_time_goal,
    stand_hours,
    stand_hours_goal,
    exercise_time_type,
    exercise_time_duration,
    exercise_time_durationUnit,
    activity_summary.created_at,
    activity_summary.updated_at

FROM activity_summary
LEFT JOIN exercise_time
USING (date);