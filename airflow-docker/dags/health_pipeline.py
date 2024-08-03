# from datetime import datetime, timedelta
import pandas as pd
import psycopg2
import glob

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.filesystem import FileSensor

default_args = {
   'owner': 'admin'
}

CYCLING_FILENAME = 'daily_cycling.csv'
HEARTRATE_FILENAME = 'daily_heart_rate.csv'
WALKING_RUNNING_FILENAME = 'daily_walking_running.csv'
CYCLING_COLS = ['start_date', 'miles', 'seconds', 'avg_mph']
HEARTRATE_COLS = ['start_date', 'beats_per_min']
WALKING_RUNNING_COLS = ['start_date', 'miles']

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

    checking_for_cycling_file = FileSensor(
        task_id = 'checking_for_cycling_file',
        filepath = 'tmp/' + CYCLING_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10 # , fs_conn_id=?
    )

    checking_for_heartrate_file = FileSensor(
        task_id = 'checking_for_heartrate_file',
        filepath = 'tmp/' + HEARTRATE_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10 # , fs_conn_id=?
    )

    checking_for_walking_running_file = FileSensor(
        task_id = 'checking_for_walking_running_file',
        filepath = 'tmp/' + WALKING_RUNNING_FILENAME,
        poke_interval = 10,
        timeout = 60 * 10 # , fs_conn_id=?
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

    delete_cycling_file = BashOperator(
        task_id = 'delete_cycling_file',
        bash_command = 'rm /opt/airflow/tmp/{0}'.format(CYCLING_FILENAME)
    )

    delete_heartrate_file = BashOperator(
        task_id = 'delete_heartrate_file',
        bash_command = 'rm /opt/airflow/tmp/{0}'.format(HEARTRATE_FILENAME)
    )

    delete_walking_running_file = BashOperator(
        task_id = 'delete_walking_running_file',
        bash_command = 'rm /opt/airflow/tmp/{0}'.format(WALKING_RUNNING_FILENAME)
    )
    
    # create_table_cycling >> checking_for_file >> insert_cycling_data 
    create_table_cycling >> create_table_heartrate  >> create_table_walking_running >> \
        checking_for_cycling_file >> checking_for_heartrate_file >> checking_for_walking_running_file >> \
        insert_cycling_data >> insert_heartrate_data >> insert_walking_running_data >> \
        delete_cycling_file >> delete_heartrate_file >> delete_walking_running_file
