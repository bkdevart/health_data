# from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import psycopg2
import glob
import json
import xml.etree.ElementTree as ET

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.filesystem import FileSensor
from airflow.models.connection import Connection
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import BranchPythonOperator


default_args = {
   'owner': 'admin'
}

CYCLING_FILENAME = 'daily_cycling.csv'
HEARTRATE_FILENAME = 'daily_heart_rate.csv'
WALKING_RUNNING_FILENAME = 'daily_walking_running.csv'
CYCLING_COLS = ['start_date', 'miles', 'seconds', 'avg_mph']
HEARTRATE_COLS = ['start_date', 'beats_per_min']
WALKING_RUNNING_COLS = ['start_date', 'miles']

def iterparse_xml():
    '''
    Main XML parsing script, streams in file and proccesses each branch into
    lists, which get converted to data frames and exported to csv files for database upload
    '''
    file = 'tmp/export.xml'

    # activity data
    date = []
    energy_burned = []
    energy_burned_goal = []
    energy_burned_unit = []
    exercise_time = []
    exercise_time_goal = []
    stand_hours = []
    stand_hours_goal = []

    # exercise time
    exercise_time_type = []
    exercise_time_date = []
    exercise_time_duration = []
    exercise_time_durationUnit = []

    for event, elem in ET.iterparse(file, events=("start", "end")):
        if event == 'end':
            # process the tag
            if elem.tag == 'ActivitySummary':
                # import pdb;pdb.set_trace()
                for item in elem.items():
                    if item[0] == 'dateComponents':
                        date.append(item[1])
                    elif item[0] == 'activeEnergyBurned':
                        energy_burned.append(item[1])
                    elif item[0] == 'activeEnergyBurnedGoal':
                        energy_burned_goal.append(item[1])
                    elif item[0] == 'activeEnergyBurnedUnit':
                        energy_burned_unit.append(item[1])
                    elif item[0] == 'appleExerciseTime':
                        exercise_time.append(item[1])
                    elif item[0] == 'appleExerciseTimeGoal':
                        exercise_time_goal.append(item[1])
                    elif item[0] == 'appleStandHours':
                        stand_hours.append(item[1])
                    elif item[0] == 'appleStandHoursGoal':
                        stand_hours_goal.append(item[1])
            if elem.tag == 'WorkoutEvent':
                for item in elem.items():
                    if item[0] == 'type':
                        exercise_time_type.append(item[1])
                    elif item[0] == 'date':
                        exercise_time_date.append(item[1])
                    elif item[0] == 'duration':
                        exercise_time_duration.append(item[1])
                    elif item[0] == 'durationUnit':
                        exercise_time_durationUnit.append(item[1])
            
            # this is the key to memory management on the server
            elem.clear()

    # create activity data data frame
    print('Creating activity data...')
    li = list(zip(date, energy_burned, energy_burned_goal,
                energy_burned_unit, exercise_time,
                exercise_time_goal, stand_hours, stand_hours_goal))
    df = pd.DataFrame(li, columns=['date',
                                'energy_burned',
                                'energy_burned_goal',
                                'energy_burned_unit',
                                'exercise_time',
                                'exercise_time_goal',
                                'stand_hours',
                                'stand_hours_goal'])
    # remove dates before 2000-01-01
    df['datetime'] = pd.to_datetime(df['date'])
    df = df[df['datetime'] > '2000-01-01']
    # drop datetime column
    df = df.drop(['datetime'], axis=1)
    # add created_at, last_updated_by
    df['created_at'] = pd.to_datetime('now')
    df['updated_at'] = pd.to_datetime('now')
    df.fillna(0, inplace=True)

    # create exercise time data frame
    print('Creating exercise time data...')
    li = list(zip(exercise_time_date, exercise_time_type,
                exercise_time_duration, exercise_time_durationUnit))
    exercise_time = pd.DataFrame(li,
                                columns=['date',
                                        'exercise_time_type',
                                        'exercise_time_duration',
                                        'exercise_time_durationUnit'])
    # remove dates before 2000-01-01
    exercise_time['datetime'] = pd.to_datetime(exercise_time['date'])
    exercise_time = exercise_time[exercise_time['datetime'] > '2000-01-01']
    # drop datetime column
    exercise_time = exercise_time.drop(['datetime'], axis=1)
    # add created_at, last_updated_by
    exercise_time['created_at'] = pd.to_datetime('now')
    exercise_time['updated_at'] = pd.to_datetime('now')
    exercise_time.fillna(0, inplace=True)

    # csv exports
    df.to_csv('tmp/activity_summary.csv', index=False)
    exercise_time.to_csv('tmp/exercise_time.csv', index=False)

# def insert_cycling_data():
#     conn = psycopg2.connect(
#         host="postgres_health",
#         database="health_db",
#         user="health_db",
#         password="health_db"
#     )

#     cur = conn.cursor()

#     for file in glob.glob('tmp/' + CYCLING_FILENAME):
#         df = pd.read_csv(file, usecols=CYCLING_COLS)

#         records = df.to_dict('records')
        
#         for record in records:
#             query = f"""INSERT INTO cycling 
#                         (start_date, miles, seconds, avg_mph) 
#                         VALUES (
#                             '{record['start_date']}', 
#                             '{record['miles']}', 
#                             '{record['seconds']}', 
#                             {record['avg_mph']})
#                     """

#             cur.execute(query)

#     conn.commit()

#     cur.close()
#     conn.close()

# def insert_heartrate_data():
#     conn = psycopg2.connect(
#         host="postgres_health",
#         database="health_db",
#         user="health_db",
#         password="health_db"
#     )

#     cur = conn.cursor()

#     for file in glob.glob('tmp/' + HEARTRATE_FILENAME):
#         df = pd.read_csv(file, usecols=HEARTRATE_COLS)

#         records = df.to_dict('records')
        
#         for record in records:
#             query = f"""INSERT INTO heartrate 
#                         (start_date, beats_per_min) 
#                         VALUES (
#                             '{record['start_date']}', 
#                             '{record['beats_per_min']}')
#                     """

#             cur.execute(query)

#     conn.commit()

#     cur.close()
#     conn.close()

# def insert_walking_running_data():
#     conn = psycopg2.connect(
#         host="postgres_health",
#         database="health_db",
#         user="health_db",
#         password="health_db"
#     )

#     cur = conn.cursor()

#     for file in glob.glob('tmp/' + WALKING_RUNNING_FILENAME):
#         df = pd.read_csv(file, usecols=WALKING_RUNNING_COLS)

#         records = df.to_dict('records')
        
#         for record in records:
#             query = f"""INSERT INTO walking_running 
#                         (start_date, miles) 
#                         VALUES (
#                             '{record['start_date']}', 
#                             '{record['miles']}')
#                     """

#             cur.execute(query)

#     conn.commit()

#     cur.close()
#     conn.close()

def insert_activity_summary_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    # for file in glob.glob('tmp/activity_summary.csv'):
    df = pd.read_csv('tmp/activity_summary.csv')

    records = df.to_dict('records')
    
    for record in records:
        query = f"""INSERT INTO activity_summary 
                    (date, energy_burned, energy_burned_goal, energy_burned_unit,
                        exercise_time, exercise_time_goal, stand_hours, stand_hours_goal,
                        created_at, updated_at) 
                    VALUES (
                        '{record['date']}',
                        '{record['energy_burned']}', 
                        '{record['energy_burned_goal']}',
                        '{record['energy_burned_unit']}', 
                        '{record['exercise_time']}',
                        '{record['exercise_time_goal']}', 
                        '{record['stand_hours']}',
                        '{record['stand_hours_goal']}', 
                        '{record['created_at']}',
                        '{record['updated_at']}')
                """

        cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()

# def export_combined_data():
#     conn = psycopg2.connect(
#         host="postgres_health",
#         database="health_db",
#         user="health_db",
#         password="health_db"
#     )
#     df =  pd.read_sql('SELECT * FROM combined_data', conn)
#     df.to_csv('output/combined_data.csv', index=False)
    
def parse_xml_file():
    XML_DATA = "tmp/export.xml"
    # Parse XML file exported from Apple Health app
    tree = ET.parse(XML_DATA)
    root = tree.getroot()

    # Store "Record" type data into Pandas.DataFrame
    records = [i.attrib for i in root.iter("Record")]
    records_df = pd.DataFrame(records)

    # Convert datetime format
    date_col = ['creationDate', 'startDate', 'endDate']
    records_df[date_col] = records_df[date_col].apply(pd.to_datetime)

    cycling_df = records_df.query("type == 'HKQuantityTypeIdentifierDistanceCycling'").copy()
    cycling_df = preprocess_exercise(cycling_df, 'cycling', exercise=True)

    walking_running_df = records_df.query("type == 'HKQuantityTypeIdentifierDistanceWalkingRunning'").copy()
    walking_running_df = preprocess_exercise(walking_running_df, 'walking_running')

    heart_rate_df = records_df.query("type == 'HKQuantityTypeIdentifierHeartRate'").copy()
    heart_rate_df = preprocess_exercise(heart_rate_df, 'heart_rate', metric='beats_per_min')

def preprocess_exercise(df, filename, metric='miles', exercise=False):
    # clean up exercise data - may want to restore device later
    df.drop(['type', 'sourceName', 'unit', 'device', 'sourceVersion'], 
                    axis=1, 
                    inplace=True)
    df.rename(columns={'value': metric, 
                       'startDate': 'start_date',
                       'endDate': 'end_date',
                       'creationDate': 'creation_date'}, inplace=True)
    df[metric] = pd.to_numeric(df[metric])
    df['creation_date'] = df['creation_date'].dt.tz_convert('US/Arizona')
    df['start_date'] = df['start_date'].dt.tz_convert('US/Arizona')
    df['end_date'] = df['end_date'].dt.tz_convert('US/Arizona')
    df.sort_values(['creation_date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    if exercise and metric=='miles':
        # calculate times, speed
        df['seconds'] = (df['end_date'] - df['start_date']).dt.total_seconds()
        df['avg_mph'] = df[metric] / (df['seconds'] / 3600)

    # export granular, focused data for analysis
    df.to_csv(f'tmp/{filename}.csv', index=False)

    if exercise and metric=='miles':
        # calculate aggregated speed - assumes miles for metric and exercise=True
        # export daily summaries for analysis
        df_date = df.groupby(df['start_date'].dt.date)[[metric, 'seconds']].sum().reset_index()
        df_date['avg_mph'] = df_date[metric] / (df_date['seconds'] / 3600)
    else:
        df_date = df.groupby(df['start_date'].dt.date)[[metric]].sum().reset_index()

    df_date.to_csv(f'cleaned_data/daily_{filename}.csv', index=False)
    return df

with DAG(
    dag_id = 'health_db_pipeline',
    description = 'Running a pipeline using a file sensor',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['pipeline', 'sensor', 'file sensor'],
    template_searchpath = '/opt/airflow/sql'
) as dag:

    parse_xml_file_task = PythonOperator(
        task_id = 'parse_xml_file_task',
        python_callable = iterparse_xml
    )

    # create_table_cycling = PostgresOperator(
    #     task_id = 'create_table_cycling',
    #     postgres_conn_id = 'postgres_health_db',
    #     sql = 'create_table_cycling.sql'
    # )

    # create_table_heartrate = PostgresOperator(
    #     task_id = 'create_table_heartrate',
    #     postgres_conn_id = 'postgres_health_db',
    #     sql = 'create_table_heartrate.sql'
    # )

    # create_table_walking_running = PostgresOperator(
    #     task_id = 'create_table_walking_running',
    #     postgres_conn_id = 'postgres_health_db',
    #     sql = 'create_table_walking_running.sql'
    # )

    # create_table_combined_data = PostgresOperator(
    #     task_id = 'create_table_combined_data',
    #     postgres_conn_id = 'postgres_health_db',
    #     sql = 'create_table_combined_data.sql'
    # )

    create_table_activity_summary = PostgresOperator(
        task_id = 'create_table_activity_summary',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_activity_summary.sql'
    )

    create_table_exercise_time = PostgresOperator(
        task_id = 'create_table_exercise_time',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_exercise_time.sql'
    )

    checking_for_xml_file = FileSensor(
        task_id = 'checking_for_xml_file',
        filepath = 'tmp/export.xml',
        poke_interval = 10,
        timeout = 60 * 10
    )

    # checking_for_cycling_file = FileSensor(
    #     task_id = 'checking_for_cycling_file',
    #     filepath = 'tmp/' + CYCLING_FILENAME,
    #     poke_interval = 10,
    #     timeout = 60 * 10
    # )

    # checking_for_heartrate_file = FileSensor(
    #     task_id = 'checking_for_heartrate_file',
    #     filepath = 'tmp/' + HEARTRATE_FILENAME,
    #     poke_interval = 10,
    #     timeout = 60 * 10
    # )

    # checking_for_walking_running_file = FileSensor(
    #     task_id = 'checking_for_walking_running_file',
    #     filepath = 'tmp/' + WALKING_RUNNING_FILENAME,
    #     poke_interval = 10,
    #     timeout = 60 * 10
    # )

    checking_for_activity_summary_file = FileSensor(
        task_id = 'checking_for_activity_summary_file',
        filepath = 'tmp/activity_summary.csv',
        poke_interval = 10,
        timeout = 60 * 10
    )

    checking_for_excercise_time_file = FileSensor(
        task_id = 'checking_for_excercise_time_file',
        filepath = 'tmp/exercise_time.csv',
        poke_interval = 10,
        timeout = 60 * 10
    )

    insert_activity_summary_data_task = PythonOperator(
        task_id = 'insert_activity_summary_data_task',
        python_callable = insert_activity_summary_data
    )
    
    # insert_cycling_data = PythonOperator(
    #     task_id = 'insert_cycling_data',
    #     python_callable = insert_cycling_data
    # )

    # insert_heartrate_data = PythonOperator(
    #     task_id = 'insert_heartrate_data',
    #     python_callable = insert_heartrate_data
    # )

    # insert_walking_running_data = PythonOperator(
    #     task_id = 'insert_walking_running_data',
    #     python_callable = insert_walking_running_data
    # )

    # combine tables using SQL and export as a csv file
    # create_table_combined = PostgresOperator(
    #     task_id = 'combine_tables',
    #     postgres_conn_id = 'postgres_health_db',
    #     sql = 'combine_tables.sql'
    # )

    # export_combined_data = PythonOperator(
    #     task_id = 'export_combined_data',
    #     python_callable = export_combined_data
    # )

    # delete_cycling_file = BashOperator(
    #     task_id = 'delete_cycling_file',
    #     bash_command = 'rm /opt/airflow/tmp/{0}'.format(CYCLING_FILENAME)
    # )

    # delete_heartrate_file = BashOperator(
    #     task_id = 'delete_heartrate_file',
    #     bash_command = 'rm /opt/airflow/tmp/{0}'.format(HEARTRATE_FILENAME)
    # )

    # delete_walking_running_file = BashOperator(
    #     task_id = 'delete_walking_running_file',
    #     bash_command = 'rm /opt/airflow/tmp/{0}'.format(WALKING_RUNNING_FILENAME)
    # )
    
    # create_table_activity_summary >> create_table_cycling >> create_table_heartrate >> \
    #     create_table_walking_running >> create_table_combined_data >> \
    #     checking_for_xml_file >> parse_xml_file_task >> checking_for_activity_summary_file >> checking_for_excercise_time_file >> \
    #     insert_activity_summary_data_task >> \
    #     [checking_for_cycling_file, checking_for_heartrate_file, checking_for_walking_running_file] >> \
    #     insert_cycling_data >> insert_heartrate_data >> insert_walking_running_data >> \
    #     create_table_combined >> export_combined_data >> \
    #     delete_cycling_file >> delete_heartrate_file >> delete_walking_running_file


    create_table_activity_summary >> create_table_exercise_time >> \
        checking_for_xml_file >> parse_xml_file_task >> \
        [checking_for_activity_summary_file, checking_for_excercise_time_file] >> \
        insert_activity_summary_data_task