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
# from airflow.models.connection import Connection
# from airflow.operators.dummy_operator import DummyOperator
# from airflow.operators.python_operator import BranchPythonOperator


default_args = {
   'owner': 'admin'
}

CYCLING_FILENAME = 'daily_cycling.csv'
HEARTRATE_FILENAME = 'daily_heart_rate.csv'
WALKING_RUNNING_FILENAME = 'daily_walking_running.csv'
CYCLING_COLS = ['start_date', 'miles', 'seconds', 'avg_mph']
HEARTRATE_COLS = ['start_date', 'beats_per_min']
WALKING_RUNNING_COLS = ['start_date', 'miles']

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

def insert_exercise_time_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    df = pd.read_csv('tmp/exercise_time.csv')

    records = df.to_dict('records')
    
    for record in records:
        query = f"""INSERT INTO exercise_time 
                    (date, exercise_time_type, exercise_time_duration, 
                        exercise_time_durationUnit, created_at, updated_at) 
                    VALUES (
                        '{record['date']}',
                        '{record['exercise_time_type']}', 
                        '{record['exercise_time_duration']}',
                        '{record['exercise_time_durationUnit']}', 
                        '{record['created_at']}',
                        '{record['updated_at']}')
                """

        cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()
    
def parse_xml_file():
    # TODO: implement user_id creation and tracking from xml data
    XML_DATA = "tmp/export.xml"

    # general data fields (explore other sections of xml later)
    # TODO: restore sourceVersion, device data by checking for null before adding
    type = [] 
    sourceName = [] 
    # sourceVersion = [] 
    # device = [] 
    unit = [] 
    creationDate = []
    startDate = [] 
    endDate = [] 
    value = []
    # value = np.array([])

    # activity_summary fields
    date = []
    energy_burned = []
    energy_burned_goal = []
    energy_burned_unit = []
    exercise_time = []
    exercise_time_goal = []
    stand_hours = []
    stand_hours_goal = []

    # exercise fields
    exercise_time_type = []
    exercise_time_date = []
    exercise_time_duration = []
    exercise_time_durationUnit = []

    # personal info fields
    birthday = ''
    sex = ''
    blood_type = ''

    print('Starting to read XML into lists')
    # Iteratively parse the XML file
    for event, elem in ET.iterparse(XML_DATA, events=('end',)):
        if elem.tag == 'Me':
            birthday = elem.attrib['HKCharacteristicTypeIdentifierDateOfBirth']
            sex = elem.attrib['HKCharacteristicTypeIdentifierBiologicalSex']
            blood_type = elem.attrib['HKCharacteristicTypeIdentifierBloodType']
        if elem.tag == "Record" and \
            (elem.attrib['type'] == 'HKQuantityTypeIdentifierDistanceCycling' or
             elem.attrib['type'] == 'HKQuantityTypeIdentifierDistanceWalkingRunning' or
             elem.attrib['type'] == 'HKQuantityTypeIdentifierHeartRate' or
             elem.attrib['type'] == 'HKQuantityTypeIdentifierStepCount' or
            #  elem.attrib['type'] == 'HKQuantityTypeIdentifierActiveEnergyBurned' or
            # TODO: adding ActiveEnergyBurned results in memory issues, find a more optimal way of doing this
             elem.attrib['type'] == 'HKQuantityTypeIdentifierBasalEnergyBurned'):
            # pull out columns of interest
            # records.append(elem.attrib)
            type.append(elem.attrib['type'])
            sourceName.append(elem.attrib['sourceName'])
            # sourceVersion.append(elem.attrib['sourceVersion'])
            # device.append(elem.attrib['device'])
            unit.append(elem.attrib['unit'])
            creationDate.append(elem.attrib['creationDate'])
            startDate.append(elem.attrib['startDate'])
            endDate.append(elem.attrib['endDate'])
            # value = np.append(value, elem.attrib['value'])
            value.append(elem.attrib['value'])
        elif elem.tag == "ActivitySummary":
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
        elif elem.tag == 'WorkoutEvent':
            for item in elem.items():
                if item[0] == 'type':
                    exercise_time_type.append(item[1])
                elif item[0] == 'date':
                    exercise_time_date.append(item[1])
                elif item[0] == 'duration':
                    exercise_time_duration.append(item[1])
                elif item[0] == 'durationUnit':
                    exercise_time_durationUnit.append(item[1])
        elem.clear()  # Clear the element to save memory

    print('finished reading XML into lists')
    # create records dataframe
    records_df = pd.DataFrame({
        'type': type,
        'sourceName': sourceName,
        'unit': unit,
        'creationDate': creationDate,
        'startDate': startDate,
        'endDate': endDate,
        'value': value
    })

    customer_info = pd.DataFrame({
        'birthday': [birthday],
        'sex': [sex],
        'blood_type': [blood_type]
    })
    customer_info.to_csv('tmp/customer.csv', index=False)

    # del individual lists here to save memory
    del type, sourceName, unit, creationDate, startDate, endDate, value

    # Convert datetime format
    date_col = ['creationDate', 'startDate', 'endDate']
    records_df[date_col] = records_df[date_col].apply(pd.to_datetime)

    # TODO: move this to another task, passing the records_df through XCOM
    # filter data from records_df
    cycling_df = records_df.query("type == 'HKQuantityTypeIdentifierDistanceCycling'").copy()
    cycling_df = preprocess_exercise(cycling_df, 'cycling', exercise=True)

    walking_running_df = records_df.query("type == 'HKQuantityTypeIdentifierDistanceWalkingRunning'").copy()
    walking_running_df = preprocess_exercise(walking_running_df, 'walking_running')

    heart_rate_df = records_df.query("type == 'HKQuantityTypeIdentifierHeartRate'").copy()
    heart_rate_df = preprocess_exercise(heart_rate_df, 'heart_rate', metric='beats_per_min')

    # HKQuantityTypeIdentifierStepCount, HKQuantityTypeIdentifierBasalEnergyBurned, HKQuantityTypeIdentifierActiveEnergyBurned
    steps_df = records_df.query("type == 'HKQuantityTypeIdentifierStepCount'").copy()
    steps_df = preprocess_exercise(steps_df, 'steps', metric='steps')

    energy_basal_df = records_df.query("type == 'HKQuantityTypeIdentifierBasalEnergyBurned'").copy()
    energy_basal_df = preprocess_exercise(energy_basal_df, 'energy_basal', metric='energy')

    # TODO: add back in once memory issue resolved
    # energy_active_df = records_df.query("type == 'HKQuantityTypeIdentifierActiveEnergyBurned'").copy()
    # energy_active_df = preprocess_exercise(energy_active_df, 'energy_active', metric='energy')

    # create activity data data frame
    print('Creating activity data...')
    li = list(zip(date, energy_burned, energy_burned_goal,
                energy_burned_unit, exercise_time,
                exercise_time_goal, stand_hours, stand_hours_goal))
    activity_df = pd.DataFrame(li, columns=['date',
                                'energy_burned',
                                'energy_burned_goal',
                                'energy_burned_unit',
                                'exercise_time',
                                'exercise_time_goal',
                                'stand_hours',
                                'stand_hours_goal'])
    # remove dates before 2000-01-01
    activity_df['datetime'] = pd.to_datetime(activity_df['date'])
    activity_df = activity_df[activity_df['datetime'] > '2000-01-01']
    # drop datetime column
    activity_df = activity_df.drop(['datetime'], axis=1)
    # add created_at, last_updated_by
    activity_df['created_at'] = pd.to_datetime('now')
    activity_df['updated_at'] = pd.to_datetime('now')
    activity_df.fillna(0, inplace=True)

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

    # activity and exercise csv exports
    activity_df.to_csv('tmp/activity_summary.csv', index=False)
    exercise_time.to_csv('tmp/exercise_time.csv', index=False)


def preprocess_exercise(df, filename, metric='miles', exercise=False):
    # clean up exercise data - may want to restore device later
    df.drop(['type', 'sourceName', 'unit',
             # 'device', 'sourceVersion'
             ], 
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

    df_date.to_csv(f'tmp/daily_{filename}.csv', index=False)
    return df

def export_combined_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )
    df =  pd.read_sql('SELECT * FROM combined_data', conn)
    df.to_csv('output/combined_data.csv', index=False)

def insert_cycling_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    for file in glob.glob('tmp/' + CYCLING_FILENAME):
        df = pd.read_csv(file, usecols=CYCLING_COLS)

        records = df.to_dict('records')
        
        for record in records:
            query = f"""INSERT INTO cycling 
                        (start_date, miles, seconds, avg_mph) 
                        VALUES (
                            '{record['start_date']}', 
                            '{record['miles']}', 
                            '{record['seconds']}', 
                            {record['avg_mph']})
                    """

            cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()

def insert_heartrate_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    for file in glob.glob('tmp/' + HEARTRATE_FILENAME):
        df = pd.read_csv(file, usecols=HEARTRATE_COLS)

        records = df.to_dict('records')
        
        for record in records:
            query = f"""INSERT INTO heartrate 
                        (start_date, beats_per_min) 
                        VALUES (
                            '{record['start_date']}', 
                            '{record['beats_per_min']}')
                    """

            cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()

def insert_walking_running_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    for file in glob.glob('tmp/' + WALKING_RUNNING_FILENAME):
        df = pd.read_csv(file, usecols=WALKING_RUNNING_COLS)

        records = df.to_dict('records')
        
        for record in records:
            query = f"""INSERT INTO walking_running 
                        (start_date, miles) 
                        VALUES (
                            '{record['start_date']}', 
                            '{record['miles']}')
                    """

            cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()

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
        python_callable = parse_xml_file
    )

    create_table_customer = PostgresOperator(
        task_id = 'create_table_customer',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_customer.sql'
    )

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

    insert_excercise_time_data_task = PythonOperator(
        task_id = 'insert_excercise_time_data_task',
        python_callable = insert_exercise_time_data
    )

    backup_csv_files = BashOperator(
        task_id = 'backup_csv_files',
        bash_command = '''
            mkdir -p /opt/airflow/output &&
            cp -f /opt/airflow/tmp/cycling.csv /opt/airflow/output/cycling.csv &&
            cp -f /opt/airflow/tmp/walking_running.csv /opt/airflow/output/walking_running.csv &&
            cp -f /opt/airflow/tmp/heart_rate.csv /opt/airflow/output/heart_rate.csv &&
            cp -f /opt/airflow/tmp/steps.csv /opt/airflow/output/steps.csv &&
            cp -f /opt/airflow/tmp/energy_basal.csv /opt/airflow/output/energy_basal.csv
            cp -f /opt/airflow/tmp/customer.csv /opt/airflow/output/customer.csv
            '''
    )

    delete_temp_csv_files = BashOperator(
        task_id = 'delete_temp_csv_files',
        bash_command = 'rm -f /opt/airflow/tmp/*.csv'
    )
    
    create_table_cycling = PostgresOperator(
        task_id = 'create_table_cycling',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_cycling.sql'
    )

    create_table_heartrate = PostgresOperator(
        task_id = 'create_table_heartrate',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_heartrate.sql'
    )

    create_table_walking_running = PostgresOperator(
        task_id = 'create_table_walking_running',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_walking_running.sql'
    )

    create_table_combined_data = PostgresOperator(
        task_id = 'create_table_combined_data',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_combined_data.sql'
    )

    checking_for_cycling_file = FileSensor(
        task_id = 'checking_for_cycling_file',
        filepath = 'tmp/' + CYCLING_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10
    )

    checking_for_heartrate_file = FileSensor(
        task_id = 'checking_for_heartrate_file',
        filepath = 'tmp/' + HEARTRATE_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10
    )

    checking_for_walking_running_file = FileSensor(
        task_id = 'checking_for_walking_running_file',
        filepath = 'tmp/' + WALKING_RUNNING_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10
    )

    insert_cycling_data = PythonOperator(
        task_id = 'insert_cycling_data',
        python_callable = insert_cycling_data
    )

    insert_heartrate_data = PythonOperator(
        task_id = 'insert_heartrate_data',
        python_callable = insert_heartrate_data
    )

    insert_walking_running_data = PythonOperator(
        task_id = 'insert_walking_running_data',
        python_callable = insert_walking_running_data
    )

    # combine tables using SQL and export as a csv file
    create_table_combined = PostgresOperator(
        task_id = 'combine_tables',
        postgres_conn_id = 'postgres_health_db',
        sql = 'combine_tables.sql'
    )

    export_combined_data = PythonOperator(
        task_id = 'export_combined_data',
        python_callable = export_combined_data
    )

    # combine_activity_exercise >> export_combined_activity_exercise_data >> create_table_combined_activity_exercise >> \
    create_table_customer >> create_table_activity_summary >> create_table_exercise_time >> \
    create_table_cycling >> create_table_heartrate >> \
    create_table_walking_running >> create_table_combined_data >> \
    checking_for_xml_file >> parse_xml_file_task >> \
    [checking_for_activity_summary_file, checking_for_excercise_time_file, checking_for_cycling_file, checking_for_heartrate_file, checking_for_walking_running_file] >> \
    insert_activity_summary_data_task >> insert_excercise_time_data_task >> \
        insert_cycling_data >> insert_heartrate_data >> insert_walking_running_data >> \
        create_table_combined >> export_combined_data >> backup_csv_files >> delete_temp_csv_files
