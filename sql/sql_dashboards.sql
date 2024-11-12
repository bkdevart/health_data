-- SUMMARY
-- All Time Longest Daily Distance
SELECT day AS day,
              REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
              ROUND(max_daily) AS max_daily
FROM
  (WITH daily_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) AS daily_total
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT day,
                            customer_id,
                            source_name,
                            REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') as activity_name,
                            unit,
                            ROUND(daily_total) as max_daily
   FROM daily_data
   WHERE (customer_id,
          source_name,
          activity_name,
          unit,
          daily_total) IN
       (SELECT customer_id,
               source_name,
               activity_name,
               unit,
               MAX(daily_total)
        FROM daily_data
        GROUP BY customer_id,
                 source_name,
                 activity_name,
                 unit)
   ORDER BY customer_id,
            source_name,
            activity_name,
            unit,
            day) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND ((source_name LIKE '%Watch%'))
ORDER BY customer_id ASC,
         max_daily DESC
LIMIT 1000;

-- Totals for Selected Dates
SELECT sum(cycling_miles) AS "Cycling Miles",
       SUM(cycling_seconds) / 3600 AS "Cycling Hours",
       sum(walking_running_miles) AS "Walking Running Miles",
       SUM(walking_running_seconds) / 3600 AS "Walking Running Hours",
       sum(steps_total) AS "Total Steps"
FROM
  (SELECT *,
          DATE(start_date) AS date
   FROM fact_health_activity_summary) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND start_date >= TO_DATE('2023-11-12', 'YYYY-MM-DD')
  AND start_date < TO_DATE('2024-11-12', 'YYYY-MM-DD')
  AND ((source_name like '%Watch%'))
ORDER BY "Cycling Miles" DESC
LIMIT 1000;

-- Weekday Cycling Walking Comparison
SELECT weekday AS weekday,
       LEFT(customer_id::text, 2) AS customer_id,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       AVG(avg_weekday) AS "AVG(avg_weekday)"
FROM
  (WITH daily_totals AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) AS daily_total
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT TO_CHAR(day, 'Day') AS weekday,
                            customer_id,
                            source_name,
                            activity_name,
                            unit,
                            AVG(daily_total) AS avg_weekday
   FROM daily_totals
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY TO_CHAR(day, 'Day'),
            customer_id,
            source_name,
            activity_name,
            unit
   ORDER BY avg_weekday DESC) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND ((source_name LIKE '%Watch%'))
GROUP BY weekday,
         LEFT(customer_id::text, 2),
         REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "AVG(avg_weekday)" DESC
LIMIT 1000;

-- Monthly Distance Totals
SELECT DATE_TRUNC('month', month) AS month,
       LEFT(customer_id::text, 2) AS customer_id,
       (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)] AS source_name,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       sum(monthly_total) AS "SUM(monthly_total)"
FROM
  (SELECT DATE_TRUNC('month', start_date) AS month,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) AS monthly_total
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('month', start_date),
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND month >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND month < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('month', month),
         LEFT(customer_id::text, 2), (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)], REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "SUM(monthly_total)" DESC
LIMIT 1000;

-- Monthly Avg Speed (MPH)
SELECT DATE_TRUNC('month', month) AS month,
       LEFT(customer_id::text, 2) AS customer_id,
       (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)] AS source_name,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       sum(avg_pace_unit_hour) AS "SUM(avg_pace_unit_hour)"
FROM
  (SELECT DATE_TRUNC('month', start_date) AS month,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) / NULLIF(SUM(duration_seconds), 0) * 3600 AS avg_pace_unit_hour
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('month', start_date),
            customer_id,
            source_name,
            activity_name,
            unit
   ORDER BY month,
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND month >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND month < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('month', month),
         LEFT(customer_id::text, 2), (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)], REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "SUM(avg_pace_unit_hour)" DESC
LIMIT 1000;

-- DAILY INTERVAL VIEWS
-- Daily Walking Cycling Total
SELECT DATE_TRUNC('day', day) AS day,
       LEFT(customer_id::text, 2) AS customer_id,
       (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)] AS source_name,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       sum(daily_total) AS "SUM(daily_total)"
FROM
  (SELECT DATE_TRUNC('day', start_date) AS day,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) AS daily_total
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('day', start_date),
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('day', day),
         LEFT(customer_id::text, 2), (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)], REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "SUM(daily_total)" DESC
LIMIT 1000;

-- Walking Cycling Intervals
SELECT DATE_TRUNC('second', start_date) AS start_date,
       LEFT(customer_id::text, 2) AS customer_id,
       source_name AS source_name,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       sum(value) AS "SUM(value)"
FROM
  (SELECT start_date,
          DATE_TRUNC('day', start_date) AS day,
          customer_id,
          (string_to_array(source_name, ' ')) [array_length(string_to_array(source_name, ' '), 1)] AS source_name,
          activity_name,
          unit,
          value
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND start_date >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND start_date < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('second', start_date),
         LEFT(customer_id::text, 2),
         source_name,
         REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "SUM(value)" DESC
LIMIT 1000;

-- DAILY COMPARISONS
-- Distance Over Time
SELECT DATE_TRUNC('day', day) AS day,
       REPLACE(activity_name, 'HKQuantityTypeIdentifierDistance', '') AS activity_name,
       sum(total_customer_1) AS user_1,
       sum(total_customer_2) AS user_2
FROM
  (WITH daily_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             activity_name,
             source_name,
             SUM(value) AS daily_total
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               activity_name,
               source_name),
        customer_comparison AS
     (SELECT day,
             customer_id,
             activity_name,
             source_name,
             SUM(daily_total) AS total_by_customer
      FROM daily_data
      GROUP BY day,
               customer_id,
               activity_name,
               source_name) SELECT cc1.day,
                                   cc1.activity_name,
                                   cc1.customer_id AS customer_id_1,
                                   cc1.total_by_customer AS total_customer_1,
                                   cc2.customer_id AS customer_id_2,
                                   cc2.total_by_customer AS total_customer_2,
                                   cc1.total_by_customer - cc2.total_by_customer AS difference
   FROM customer_comparison cc1
   JOIN customer_comparison cc2 ON cc1.day = cc2.day
   AND cc1.customer_id > cc2.customer_id
   ORDER BY cc1.day,
            cc1.activity_name,
            cc1.customer_id,
            cc2.customer_id) AS virtual_table
WHERE day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
GROUP BY DATE_TRUNC('day', day),
         REPLACE(activity_name, 'HKQuantityTypeIdentifierDistance', '')
ORDER BY user_1 DESC
LIMIT 10000;

-- Distance Difference
SELECT day AS day,
              ROUND(CAST(difference as NUMERIC), 2) AS difference,
              activity_name AS activity_name
FROM
  (WITH daily_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             activity_name,
             source_name,
             SUM(value) AS daily_total
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               activity_name,
               source_name),
        customer_comparison AS
     (SELECT day,
             customer_id,
             activity_name,
             source_name,
             SUM(daily_total) AS total_by_customer
      FROM daily_data
      GROUP BY day,
               customer_id,
               activity_name,
               source_name) SELECT cc1.day,
                                   cc1.activity_name,
                                   cc1.customer_id AS customer_id_1,
                                   cc1.total_by_customer AS total_customer_1,
                                   cc2.customer_id AS customer_id_2,
                                   cc2.total_by_customer AS total_customer_2,
                                   cc1.total_by_customer - cc2.total_by_customer AS difference
   FROM customer_comparison cc1
   JOIN customer_comparison cc2 ON cc1.day = cc2.day
   AND cc1.customer_id > cc2.customer_id
   ORDER BY cc1.day,
            cc1.activity_name,
            cc1.customer_id,
            cc2.customer_id) AS virtual_table
WHERE day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
LIMIT 1000;

-- Speed Over Time
SELECT DATE_TRUNC('day', day) AS day,
       REPLACE(activity_name, 'HKQuantityTypeIdentifierDistance', '') AS activity_name,
       sum(avg_pace_customer_1) AS user_1,
       sum(avg_pace_customer_2) AS user_2
FROM
  (WITH pace_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) / NULLIF(SUM(duration_seconds), 0) * 3600 AS avg_pace_unit_hour
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT p1.day,
                            p1.activity_name,
                            p1.customer_id AS customer_id_1,
                            p1.avg_pace_unit_hour AS avg_pace_customer_1,
                            p2.customer_id AS customer_id_2,
                            p2.avg_pace_unit_hour AS avg_pace_customer_2,
                            p1.avg_pace_unit_hour - p2.avg_pace_unit_hour AS pace_difference
   FROM pace_data p1
   JOIN pace_data p2 ON p1.day = p2.day
   AND p1.activity_name = p2.activity_name
   AND p1.customer_id > p2.customer_id
   ORDER BY day,
            activity_name) AS virtual_table
WHERE day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
GROUP BY DATE_TRUNC('day', day),
         REPLACE(activity_name, 'HKQuantityTypeIdentifierDistance', '')
ORDER BY user_1 DESC
LIMIT 1000;

-- Speed Difference
SELECT day AS day,
              ROUND(CAST(pace_difference AS NUMERIC), 2) AS difference,
              activity_name AS activity_name
FROM
  (WITH pace_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) / NULLIF(SUM(duration_seconds), 0) * 3600 AS avg_pace_unit_hour
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT p1.day,
                            p1.activity_name,
                            p1.customer_id AS customer_id_1,
                            p1.avg_pace_unit_hour AS avg_pace_customer_1,
                            p2.customer_id AS customer_id_2,
                            p2.avg_pace_unit_hour AS avg_pace_customer_2,
                            p1.avg_pace_unit_hour - p2.avg_pace_unit_hour AS pace_difference
   FROM pace_data p1
   JOIN pace_data p2 ON p1.day = p2.day
   AND p1.activity_name = p2.activity_name
   AND p1.customer_id > p2.customer_id
   ORDER BY day,
            activity_name) AS virtual_table
WHERE day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
LIMIT 1000;

-- MONTHLY COMPARISONS
-- Monthly Distance Difference
SELECT month AS month,
                REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
                ROUND(CAST(monthly_total AS NUMERIC), 2) AS monthly_total
FROM
  (SELECT DATE_TRUNC('month', start_date) AS month,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) AS monthly_total
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('month', start_date),
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND month >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND month < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
LIMIT 1000;

-- Monthly Speed Comparison
SELECT DATE_TRUNC('month', month) AS month,
       activity_name AS activity_name,
       sum(avg_mph_cs1) AS "SUM(avg_mph_cs1)",
       sum(avg_mph_cs2) AS "SUM(avg_mph_cs2)"
FROM
  (WITH pace_data AS
     (SELECT DATE_TRUNC('month', start_date) AS month,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) / NULLIF(SUM(duration_seconds), 0) * 3600 AS avg_pace_unit_hour
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('month', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT p1.month,
                            p1.activity_name,
                            p1.customer_id AS customer_id_1,
                            p1.avg_pace_unit_hour AS avg_mph_cs1,
                            p2.customer_id AS customer_id_2,
                            p2.avg_pace_unit_hour AS avg_mph_cs2,
                            p1.avg_pace_unit_hour - p2.avg_pace_unit_hour AS difference
   FROM pace_data p1
   JOIN pace_data p2 ON p1.month = p2.month
   AND p1.activity_name = p2.activity_name
   AND p1.customer_id > p2.customer_id
   ORDER BY month,
            activity_name) AS virtual_table
WHERE month >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND month < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
GROUP BY DATE_TRUNC('month', month),
         activity_name
ORDER BY "SUM(avg_mph_cs1)" DESC
LIMIT 10000;

-- Monthly Speed Comparison
SELECT month AS month,
                REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
                ROUND(CAST(difference AS NUMERIC), 2) AS difference
FROM
  (WITH pace_data AS
     (SELECT DATE_TRUNC('month', start_date) AS month,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) / NULLIF(SUM(duration_seconds), 0) * 3600 AS avg_pace_unit_hour
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
        AND source_name LIKE '%Watch%'
      GROUP BY DATE_TRUNC('month', start_date),
               customer_id,
               source_name,
               activity_name,
               unit) SELECT p1.month,
                            p1.activity_name,
                            p1.customer_id AS customer_id_1,
                            p1.avg_pace_unit_hour AS avg_mph_cs1,
                            p2.customer_id AS customer_id_2,
                            p2.avg_pace_unit_hour AS avg_mph_cs2,
                            p1.avg_pace_unit_hour - p2.avg_pace_unit_hour AS difference
   FROM pace_data p1
   JOIN pace_data p2 ON p1.month = p2.month
   AND p1.activity_name = p2.activity_name
   AND p1.customer_id > p2.customer_id
   ORDER BY month,
            activity_name) AS virtual_table
WHERE month >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND month < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
LIMIT 1000;

-- ANALYTICAL VIEWS
-- Activity Heatmap
SELECT DATE_TRUNC('day', day) AS __timestamp,
       sum(daily_total) AS "SUM(daily_total)"
FROM
  (SELECT DATE_TRUNC('day', start_date) AS day,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) AS daily_total
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('day', start_date),
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
GROUP BY DATE_TRUNC('day', day)
LIMIT 50000;

-- Daily Distance Distribution
SELECT DATE_TRUNC('day', day) AS day,
       LEFT(customer_id::text, 2) AS customer_id,
       (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)] AS source_name,
       REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
       sum(daily_total) AS "SUM(daily_total)"
FROM
  (SELECT DATE_TRUNC('day', start_date) AS day,
          customer_id,
          source_name,
          activity_name,
          unit,
          SUM(value) AS daily_total
   FROM fact_health_activity_base
   LEFT JOIN dim_activity_type USING (activity_type_id)
   WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                           'HKQuantityTypeIdentifierDistanceWalkingRunning')
   GROUP BY DATE_TRUNC('day', start_date),
            customer_id,
            source_name,
            activity_name,
            unit) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('day', day),
         LEFT(customer_id::text, 2), (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)], REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
LIMIT 50000;

-- Outliers
SELECT DATE_TRUNC('day', day) AS day,
       replace(activity_name, 'HKQuantityTypeIdentifierDistance', '') AS activity_name,
       sum(daily_total) AS "Miles"
FROM
  (WITH daily_data AS
     (SELECT DATE_TRUNC('day', start_date) AS day,
             customer_id,
             source_name,
             activity_name,
             unit,
             SUM(value) AS daily_total
      FROM fact_health_activity_base
      LEFT JOIN dim_activity_type USING (activity_type_id)
      WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                              'HKQuantityTypeIdentifierDistanceWalkingRunning')
      GROUP BY DATE_TRUNC('day', start_date),
               customer_id,
               source_name,
               activity_name,
               unit),
        stats AS
     (SELECT customer_id,
             source_name,
             activity_name,
             unit,
             AVG(daily_total) AS avg_distance,
             STDDEV(daily_total) AS stddev_distance
      FROM daily_data
      GROUP BY customer_id,
               source_name,
               activity_name,
               unit) SELECT d.day,
                            d.customer_id,
                            d.source_name,
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
   FROM daily_data d
   JOIN stats s ON d.customer_id = s.customer_id
   AND d.source_name = s.source_name
   AND d.activity_name = s.activity_name
   AND d.unit = s.unit
   ORDER BY d.customer_id,
            d.source_name,
            d.activity_name,
            d.unit,
            d.day) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
  AND outlier_status IN ('High Outlier',
                         'Low Outlier')
  AND day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
  AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('day', day),
         replace(activity_name, 'HKQuantityTypeIdentifierDistance', '')
ORDER BY count(DISTINCT day) DESC
LIMIT 1000;

-- Daily Distance Change Rate
SELECT DATE_TRUNC('day', day) AS day,
    LEFT(customer_id::text, 2) AS customer_id,
    (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)] AS source_name,
    REPLACE(activity_name, 'HKQuantityTypeIdentifier', '') AS activity_name,
    sum(percentage_change) AS "SUM(percentage_change)"
FROM
(WITH daily_data AS
    (SELECT DATE_TRUNC('day', start_date) AS day,
            customer_id,
            source_name,
            activity_name,
            unit,
            SUM(value) AS daily_total
    FROM fact_health_activity_base
    LEFT JOIN dim_activity_type USING (activity_type_id)
    WHERE activity_name IN ('HKQuantityTypeIdentifierDistanceCycling',
                            'HKQuantityTypeIdentifierDistanceWalkingRunning')
    GROUP BY DATE_TRUNC('day', start_date),
            customer_id,
            source_name,
            activity_name,
            unit),
    days AS
    (SELECT GENERATE_SERIES(
        (SELECT MIN(start_date::date)
        FROM fact_health_activity_base),
        (SELECT MAX(start_date::date)
        FROM fact_health_activity_base), '1 day'::interval) AS day) 
        SELECT d.day,
            dd.customer_id,
            dd.source_name,
            dd.activity_name,
            dd.unit,
            COALESCE(dd.daily_total, 0) AS daily_total,
            LAG(COALESCE(dd.daily_total, 0)) 
                OVER (PARTITION BY dd.customer_id,
                            dd.source_name,
                            dd.activity_name,
                            dd.unit
                ORDER BY d.day,
                        dd.customer_id,
                        dd.source_name,
                        dd.activity_name,
                        dd.unit) AS previous_day_total,
                (CASE
                    WHEN LAG(COALESCE(dd.daily_total, 0)) 
                        OVER (PARTITION BY dd.customer_id,
                                    dd.source_name,
                                    dd.activity_name,
                                    dd.unit
                        ORDER BY d.day,
                                dd.customer_id,
                                dd.source_name,
                                dd.activity_name,
                                dd.unit) = 0 THEN NULL
                    ELSE ((COALESCE(dd.daily_total, 0) - LAG(COALESCE(dd.daily_total, 0)) 
                        OVER (PARTITION BY dd.customer_id,
                                    dd.source_name,
                                    dd.activity_name,
                                    dd.unit
                        ORDER BY d.day,
                                dd.customer_id,
                                dd.source_name,
                                dd.activity_name,
                                dd.unit)) / NULLIF(LAG(COALESCE(dd.daily_total, 0)) 
                        OVER (PARTITION BY dd.customer_id, dd.source_name, dd.activity_name, dd.unit
                        ORDER BY d.day, dd.customer_id, dd.source_name, dd.activity_name, dd.unit), 0)) * 100
                END) AS percentage_change
FROM days d
LEFT JOIN daily_data dd ON d.day = dd.day
ORDER BY dd.customer_id,
        dd.source_name,
        dd.activity_name,
        dd.unit,
        d.day) AS virtual_table
WHERE customer_id IN ('8daad25d-a852-4624-b22f-e99b86929a84')
AND day >= TO_TIMESTAMP('2023-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
AND day < TO_TIMESTAMP('2024-11-12 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.US')
AND ((source_name LIKE '%Watch%'))
GROUP BY DATE_TRUNC('day', day),
        LEFT(customer_id::text, 2), (string_to_array(source_name, ' '))[array_length(string_to_array(source_name, ' '), 1)], REPLACE(activity_name, 'HKQuantityTypeIdentifier', '')
ORDER BY "SUM(percentage_change)" DESC
LIMIT 1000;