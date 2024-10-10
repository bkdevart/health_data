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

-- Outliers in daily totals
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
),
stats AS (
    SELECT 
        customer_id,
        activity_name,
        unit,
        AVG(daily_total) AS avg_distance,
        STDDEV(daily_total) AS stddev_distance
    FROM 
        daily_data
    GROUP BY 
        customer_id,
        activity_name,
        unit
)
SELECT 
    d.day,
    d.customer_id,
    d.activity_name,
    d.unit,
    d.daily_total,
    s.avg_distance,
    s.stddev_distance,
    CASE 
        WHEN d.daily_total > s.avg_distance + 2 * s.stddev_distance THEN 'High Outlier'
        WHEN d.daily_total < s.avg_distance - 2 * s.stddev_distance THEN 'Low Outlier'
        ELSE 'Normal'
    END AS outlier_status
FROM 
    daily_data d
JOIN 
    stats s 
ON 
    d.customer_id = s.customer_id 
    AND d.activity_name = s.activity_name 
    AND d.unit = s.unit
ORDER BY 
    d.customer_id, d.activity_name, d.unit, d.day;

-- peak performance day by activity, customer
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
    daily_total
FROM 
    daily_data
WHERE 
    (customer_id, activity_name, unit, daily_total) IN (
        SELECT 
            customer_id, 
            activity_name, 
            unit, 
            MAX(daily_total)
        FROM 
            daily_data
        GROUP BY 
            customer_id, activity_name, unit
    )
ORDER BY 
    customer_id, activity_name, unit, day;
