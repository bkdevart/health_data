-- ANALYSIS QUERIES --
-- daily totals
SELECT 
    DATE_TRUNC('day', start_date) AS day,
    activity_name,
    unit,
    SUM(value) AS daily_total
FROM 
    fact_health_activity_base LEFT JOIN
    dim_activity_type USING (activity_type_id)
WHERE 
    activity_name != 'HKQuantityTypeIdentifierHeartRate'
GROUP BY 
    DATE_TRUNC('day', start_date),
    customer_id,
    activity_name,
    unit
ORDER BY 
    day;

-- weekly totals
SELECT 
    DATE_TRUNC('week', start_date) AS week,
    customer_id,
    activity_name,
    unit,
    SUM(value) AS weekly_total
FROM 
    fact_health_activity_base LEFT JOIN
    dim_activity_type USING (activity_type_id)
-- spotcheck a week
-- WHERE DATE_TRUNC('week', start_date) = '2024-08-05'
GROUP BY 
    DATE_TRUNC('week', start_date),
    customer_id,
    activity_name,
    unit
ORDER BY 
    week;

-- monthly totals
SELECT 
    DATE_TRUNC('month', start_date) AS month,
    customer_id,
    activity_name,
    unit,
    SUM(value) AS weekly_total
FROM 
    fact_health_activity_base LEFT JOIN
    dim_activity_type USING (activity_type_id)
-- spotcheck a month
-- WHERE DATE_TRUNC('month', start_date) = '2024-08-01'
GROUP BY 
    DATE_TRUNC('month', start_date),
    customer_id,
    activity_name,
    unit
ORDER BY 
    month;

-- moving averages for daily totals
WITH daily_data AS (
  SELECT 
    DATE_TRUNC('day', start_date) AS day,
    customer_id,
    activity_name,
    unit,
    SUM(value) AS daily_total
  FROM 
    fact_health_activity_base
  LEFT JOIN
    dim_activity_type USING (activity_type_id)
  GROUP BY 
    DATE_TRUNC('day', start_date),
    customer_id,
    activity_name,
    unit
)
SELECT 
  day,
  customer_id,
  activity_name,
  unit,
  AVG(daily_total) OVER (
      PARTITION BY customer_id, activity_name, unit 
      ORDER BY day 
      ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) AS moving_avg_daily_total
FROM 
  daily_data
ORDER BY 
  customer_id, activity_name, unit, day;

-- daily distance change rate
WITH daily_data AS (
    SELECT 
        DATE_TRUNC('day', start_date) AS day,
        customer_id,
        activity_name,
        unit,
        SUM(value) AS daily_total
    FROM 
        fact_health_activity_base
    LEFT JOIN
        dim_activity_type USING (activity_type_id)
    GROUP BY 
        DATE_TRUNC('day', start_date),
        customer_id,
        activity_name,
        unit
)
SELECT 
    day,
    customer_id,
    activity_name,
    unit,
    daily_total,
    LAG(daily_total) OVER (PARTITION BY customer_id, activity_name, unit ORDER BY day) AS previous_day_total,
    ((daily_total - LAG(daily_total) OVER (PARTITION BY customer_id, activity_name, unit ORDER BY day)) 
     / NULLIF(LAG(daily_total) OVER (PARTITION BY customer_id, activity_name, unit ORDER BY day), 0)) * 100 AS percentage_change
FROM 
    daily_data
ORDER BY 
    customer_id, activity_name, unit, day;

-- cumulative distance over time
WITH daily_data AS (
    SELECT 
        DATE_TRUNC('day', start_date) AS day,
        customer_id,
        activity_name,
        unit,
        SUM(value) AS daily_total
    FROM 
        fact_health_activity_base LEFT JOIN
        dim_activity_type USING (activity_type_id)
    GROUP BY 
        DATE_TRUNC('day', start_date),
        customer_id,
        activity_name,
        unit
)
SELECT 
    day,
    customer_id,
    activity_name,
    unit,
    SUM(daily_total) OVER (PARTITION BY customer_id, activity_name, unit ORDER BY day) AS cumulative_total
FROM 
    daily_data
ORDER BY 
    customer_id, activity_name, unit, day;
