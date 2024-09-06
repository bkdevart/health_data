from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.utils.dates import days_ago
from airflow.operators.dummy import DummyOperator
from datetime import datetime

default_args = {
   'owner': 'admin'
}

def branch_func(**kwargs):
    # Replace this condition with your logic
    condition = True  # Example condition

    if condition:
        return 'last_task'
    else:
        return 'next_task'


with DAG(
    dag_id = 'branching_testing',
    description = 'Running a pipeline using a file sensor',
    default_args = default_args,
    start_date = days_ago(1),
    schedule_interval = '@once',
    tags = ['pipeline', 'sensor', 'file sensor'],
    template_searchpath = '/opt/airflow/sql'
) as dag:

    # Branching Task
    branching = BranchPythonOperator(
        task_id='branching_task',
        python_callable=branch_func,
        provide_context=True
    )

    # Task that will be executed if condition is True
    last_task = DummyOperator(
        task_id='last_task'
    )

    # Task that will be executed if condition is False
    next_task = DummyOperator(
        task_id='next_task'
    )

    # A task that follows the "next_task"
    final_task = DummyOperator(
        task_id='final_task'
    )

    # Task dependencies
    branching >> [last_task, next_task]
    next_task >> final_task
