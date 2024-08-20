# from datetime import datetime, timedelta
import pandas as pd
# import numpy as np
import psycopg2
# import glob
# import json
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

def extract_daily_summary_to_csv():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )
    df = pd.read_sql('SELECT * FROM fact_health_activity_summary;', conn)
    df.to_csv('tmp/fact_health_activity_summary.csv', index=False)
    conn.close()

def extract_activity_detail_to_csv():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )
    df = pd.read_sql("SELECT * FROM fact_health_activity_detail WHERE activity_name != 'HKQuantityTypeIdentifierHeartRate';", conn)
    df.to_csv('tmp/fact_health_activity_detail.csv', index=False)
    conn.close()

def pull_customer_id(**kwargs):
    ti = kwargs["ti"]

    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    df = pd.read_sql('SELECT customer_id FROM dim_customer;', conn)
    customer_id = df['customer_id'].values[0]
    ti.xcom_push('customer_id', customer_id)

def insert_dim_activity_type_data(**kwargs):
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )
    cur = conn.cursor()

    # read from XCOM list of activity types
    ti = kwargs["ti"]
    activity_types = ti.xcom_pull(task_ids='parse_xml_file_task', key='activity_types')
    df = pd.DataFrame({'activity_name': activity_types})

    records = df.to_dict('records')
    
    for record in records:
        query = f"""INSERT INTO dim_activity_type 
                    (activity_name) 
                    VALUES (
                        '{record['activity_name']}'
                        )
                """

        cur.execute(query)

    conn.commit()

    # select from the table to get db-assigned ids and push to XCOM
    df = pd.read_sql('SELECT * FROM dim_activity_type;', conn)
    activity_types_dict = df.to_dict()
    # activity_types_string = json.dumps(activity_types_dict)
    ti.xcom_push('activity_types', activity_types_dict)

    cur.close()
    conn.close()
    

def insert_activity_summary_data(**kwargs):
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    # for file in glob.glob('tmp/activity_summary.csv'):
    df = pd.read_csv('tmp/activity_summary.csv')
    
    # add customer_id
    ti = kwargs["ti"]
    customer_id = ti.xcom_pull(task_ids='pull_customer_id', key='customer_id')
    df['customer_id'] = customer_id

    records = df.to_dict('records')
    
    for record in records:
        query = f"""INSERT INTO activity_summary 
                    (customer_id, date, energy_burned, energy_burned_goal, energy_burned_unit,
                        exercise_time, exercise_time_goal, stand_hours, stand_hours_goal,
                        created_at, updated_at) 
                    VALUES (
                        '{record['customer_id']}',
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
    
def parse_xml_file(**kwargs):
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

    # TODO: adding ActiveEnergyBurned results in memory issues, find a more optimal way of doing this
    activity_types = ['HKQuantityTypeIdentifierDistanceCycling', 
                      'HKQuantityTypeIdentifierDistanceWalkingRunning',
                      'HKQuantityTypeIdentifierHeartRate', 
                      'HKQuantityTypeIdentifierStepCount',
                      'HKQuantityTypeIdentifierBasalEnergyBurned',
                    #   'HKQuantityTypeIdentifierActiveEnergyBurned',
                      ]
    # push activity_types to XCOM
    ti = kwargs["ti"]
    ti.xcom_push('activity_types', activity_types)

    print('Starting to read XML into lists')
    # Iteratively parse the XML file
    for event, elem in ET.iterparse(XML_DATA, events=('end',)):
        if elem.tag == 'Me':
            birthday = elem.attrib['HKCharacteristicTypeIdentifierDateOfBirth']
            sex = elem.attrib['HKCharacteristicTypeIdentifierBiologicalSex']
            blood_type = elem.attrib['HKCharacteristicTypeIdentifierBloodType']
        if elem.tag == "Record" and elem.attrib['type'] in activity_types:
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

    print('Finished reading XML into lists')
    # create records dataframe
    records_df = pd.DataFrame({
        'type': type,
        'source_name': sourceName,
        'unit': unit,
        'creation_date': creationDate,
        'start_date': startDate,
        'end_date': endDate,
        'value': value
    })

    # TODO: move this to XCOM
    customer_info = pd.DataFrame({
        'birthday': [birthday],
        'sex': [sex],
        'blood_type': [blood_type]
    })
    customer_info.to_csv('tmp/customer.csv', index=False)

    # del individual lists here to save memory
    del type, sourceName, unit, creationDate, startDate, endDate, value

    # Convert datetime format
    date_col = ['creation_date', 'start_date', 'end_date']
    records_df[date_col] = records_df[date_col].apply(pd.to_datetime)

    # TODO: passing the records_df through XCOM? likely too large
    print('Writing fact_health_activity_base data to disk')
    # push record_df to .csv
    records_df.to_csv('tmp/fact_health_activity_base.csv', index=False)

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

def insert_customer_data():
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    df = pd.read_csv('tmp/customer.csv')

    records = df.to_dict('records')
    
    for record in records:
        query = f"""INSERT INTO dim_customer 
                    (birthday, sex, blood_type) 
                    VALUES (
                        '{record['birthday']}', 
                        '{record['sex']}', 
                        '{record['blood_type']}')
                """

        cur.execute(query)

    conn.commit()

    cur.close()
    conn.close()

def insert_fact_health_activity_base(**kwargs):
    conn = psycopg2.connect(
        host="postgres_health",
        database="health_db",
        user="health_db",
        password="health_db"
    )

    cur = conn.cursor()

    # pull activity ID for cycling activity and add to data
    ti = kwargs["ti"]
    activity_types = ti.xcom_pull(task_ids='insert_dim_activity_type_data', key='activity_types')
    activity_types = pd.DataFrame(activity_types)
    # print(activity_types.head())

    # import fact_health_activity data
    date_col = ['creation_date', 'start_date', 'end_date']
    # records_df[date_col] = records_df[date_col].apply(pd.to_datetime)
    print('reading fact_health_activity.csv')
    df = pd.read_csv('tmp/fact_health_activity_base.csv', parse_dates=date_col)
    # map activity_id values from activity_types using activity_name column, and remove activity_name column
    df['activity_type_id'] = df['type'].map(activity_types.set_index('activity_name')['activity_type_id'])
    df.drop('type', axis=1, inplace=True)

    # fix apostrophes in sourceName columns to avoid SQL insert errors
    df['source_name'] = df['source_name'].str.replace("'", "''")
    # TODO: replace HKQuantityTypeIdentifier prefix with null in activity_name (need to do in dim_activity_type too)
    # df['HKQuantityTypeIdentifier'] = df['HKQuantityTypeIdentifier'].str.replace("HKQuantityTypeIdentifier", "")
    # add customer id to data
    customer_id = ti.xcom_pull(task_ids='pull_customer_id', key='customer_id')
    df['customer_id'] = customer_id
    df['updated_at'] = pd.to_datetime('now')
    
    df['duration_seconds'] = (df['end_date'] - df['start_date']).dt.total_seconds()

    records = df.to_dict('records')
    print('Inserting into fact_health_activity table')
    for record in records:
        query = f"""INSERT INTO fact_health_activity_base 
                    (customer_id, activity_type_id, 
                    source_name, unit, value, duration_seconds,
                    start_date, creation_date, end_date, updated_at) 
                    VALUES (
                        '{record['customer_id']}', 
                        '{record['activity_type_id']}', 
                        '{record['source_name']}',
                        '{record['unit']}',
                        {record['value']},
                        {record['duration_seconds']},
                        '{record['start_date']}',
                        '{record['creation_date']}',
                        '{record['end_date']}',
                        '{record['updated_at']}'
                        )
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

    create_table_dim_customer = PostgresOperator(
        task_id = 'create_table_dim_customer',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_dim_customer.sql'
    )

    create_table_dim_activity_type = PostgresOperator(
        task_id = 'create_table_dim_activity_type',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_dim_activity_type.sql'
    )

    create_fact_health_activity_base = PostgresOperator(
        task_id = 'create_fact_health_activity_base',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_fact_health_activity_base.sql'
    )

    create_fact_health_activity_daily = PostgresOperator(
        task_id = 'create_fact_health_activity_daily',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_fact_health_activity_daily.sql'
    )

    create_fact_health_activity_detail = PostgresOperator(
        task_id = 'create_fact_health_activity_detail',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_fact_health_activity_detail.sql'
    )

    checking_for_xml_file = FileSensor(
        task_id = 'checking_for_xml_file',
        filepath = 'tmp/export.xml',
        poke_interval = 10,
        timeout = 60 * 10
    )

    checking_for_fact_health_activity_file = FileSensor(
        task_id = 'checking_for_fact_health_activity_file',
        filepath = 'tmp/fact_health_activity_base.csv',
        poke_interval = 10,
        timeout = 60 * 10
    )

    backup_csv_files = BashOperator(
        task_id = 'backup_csv_files',
        bash_command = '''
            mkdir -p /opt/airflow/output &&
            cp -f /opt/airflow/tmp/fact_health_activity_summary.csv /opt/airflow/output/fact_health_activity_summary.csv
            cp -f /opt/airflow/tmp/fact_health_activity_detail.csv /opt/airflow/output/fact_health_activity_detail.csv
            '''
    )

    delete_temp_csv_files = BashOperator(
        task_id = 'delete_temp_csv_files',
        bash_command = 'rm -f /opt/airflow/tmp/*.csv'
    )

    pull_customer_id = PythonOperator(
        task_id = 'pull_customer_id',
        python_callable = pull_customer_id
    )

    insert_customer_data = PythonOperator(
        task_id = 'insert_customer_data',
        python_callable = insert_customer_data
    )

    insert_dim_activity_type_data = PythonOperator(
        task_id = 'insert_dim_activity_type_data',
        python_callable = insert_dim_activity_type_data
    )

    insert_fact_health_activity_base = PythonOperator(
        task_id = 'insert_fact_health_activity_base',
        python_callable = insert_fact_health_activity_base
    )

    insert_fact_health_activity_daily = PostgresOperator(
        task_id = 'insert_fact_health_activity_daily',
        postgres_conn_id = 'postgres_health_db',
        sql = 'insert_fact_health_activity_daily.sql'
    )

    create_fact_health_activity_summary = PostgresOperator(
        task_id = 'create_fact_health_activity_summary',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_fact_health_activity_summary.sql'
    )

    insert_fact_health_activity_summary = PostgresOperator(
        task_id = 'insert_fact_health_activity_summary',
        postgres_conn_id = 'postgres_health_db',
        sql = 'insert_fact_health_activity_summary.sql'
    )

    insert_fact_health_activity_detail = PostgresOperator(
        task_id = 'insert_fact_health_activity_detail',
        postgres_conn_id = 'postgres_health_db',
        sql = 'insert_fact_health_activity_detail.sql'
    )

    extract_daily_summary_to_csv = PythonOperator(
        task_id = 'extract_daily_summary_to_csv',
        python_callable = extract_daily_summary_to_csv
    )

    extract_activity_detail_to_csv = PythonOperator(
        task_id = 'extract_activity_detail_to_csv',
        python_callable = extract_activity_detail_to_csv
    )

    create_table_dim_customer >> create_table_dim_activity_type >> create_fact_health_activity_base >> create_fact_health_activity_daily >>\
    create_fact_health_activity_summary >> create_fact_health_activity_detail >> checking_for_xml_file >> \
    parse_xml_file_task >> [checking_for_fact_health_activity_file] >> \
    insert_customer_data >> pull_customer_id >> insert_dim_activity_type_data >> insert_fact_health_activity_base >> \
    insert_fact_health_activity_daily >> insert_fact_health_activity_summary >> insert_fact_health_activity_detail >> \
    extract_daily_summary_to_csv >> extract_activity_detail_to_csv >> backup_csv_files >> delete_temp_csv_files
