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

from config import postgres_pwd

default_args = {
   'owner': 'admin'
}

FILE_PATH = '/Users/Brandon/airflow/tmp/daily_cycling.csv'
FILE_COLS = ['start_date', 'miles', 'seconds', 'avg_mph']

OUTPUT_FILE = '/Users/Brandon/airflow/output/{}.csv'

def insert_cycling_data():
    conn = psycopg2.connect(
        host="localhost",
        database="health_db",
        user="postgres",
        password=postgres_pwd
    )

    cur = conn.cursor()

    for file in glob.glob(FILE_PATH):
        df = pd.read_csv(file, usecols=FILE_COLS)

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


with DAG(
    dag_id = 'health_db_pipeline',
    description = 'Running a pipeline using a file sensor',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['pipeline', 'sensor', 'file sensor'],
    template_searchpath = '/Users/Brandon/airflow/sql_statements'
) as dag:
    create_table_cycling = PostgresOperator(
        task_id = 'create_table_cycling',
        postgres_conn_id = 'postgres_health_db',
        sql = 'create_table_cycling.sql'
    )

    checking_for_file = FileSensor(
        task_id = 'checking_for_file',
        filepath = FILE_PATH,
        poke_interval = 10,
        timeout = 60 * 10
    )
    
    insert_cycling_data = PythonOperator(
        task_id = 'insert_cycling_data',
        python_callable = insert_cycling_data
    )

    delete_file = BashOperator(
        task_id = 'delete_file',
        bash_command = 'rm {0}'.format(FILE_PATH)
    )
    
    create_table_cycling >> checking_for_file >> insert_cycling_data >> delete_file
