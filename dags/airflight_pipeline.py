import os
import sys
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from datetime import datetime, timedelta

# Pastikan /opt/airflow sudah ada di sys.path sebelum import scripts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from scripts.extract_data import extract_etl
from scripts.transform_data import transform_etl
from scripts.load_data import load_etl

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'airflights_etl_pipeline',
    default_args=default_args,
    description='ETL pipeline',
    schedule_interval='*/2 * * * *',  # setiap 2 menit
    catchup=False
) as dag:

    # TaskGroup untuk paralel extract
    with TaskGroup('extract_task', tooltip='Extract Batch') as extract_task:
        # prev_task = None
        for i in range(1, 6):  # contoh 5 batch
            extract_data = PythonOperator(
                task_id=f'extract{i}',
                python_callable=extract_etl,
                op_kwargs={
                    'input_file': '/opt/airflow/data/hflights.csv',
                    'output_file': f'/opt/airflow/data/output/extracted_batch{i}.csv',
                    'batch_number': i,
                    'batch_size': 5000
                }
            )
            # if prev_task:
            #     prev_task >> extract_data
            # prev_task = extract_data

    transform_data = PythonOperator(
        task_id='transform',
        python_callable=transform_etl,
        op_kwargs={
            'input_file': [
                '/opt/airflow/data/output/extracted_batch1.csv',
                '/opt/airflow/data/output/extracted_batch2.csv',
                '/opt/airflow/data/output/extracted_batch3.csv',
                '/opt/airflow/data/output/extracted_batch4.csv',
                '/opt/airflow/data/output/extracted_batch5.csv',
            ],
            # 'output_file1': '/opt/airflow/data/output/transformed.parquet',
            'output_file_summary': (
                '/opt/airflow/data/output/hflights_summary.parquet'
            ),
            'output_file_full': (
                '/opt/airflow/data/output/hflights_day.parquet'
            ),
        }
    )

    load_data = PythonOperator(
        task_id='load',
        python_callable=load_etl,
        op_kwargs={
            'input_file': '/opt/airflow/data/output/hflights_summary.parquet',
            'input_file_day': '/opt/airflow/data/output/hflights_full.parquet',
            'table_name': 'flights_summary',
            'table_name_full': 'flights_timeofday',
            'db_user': 'postgres',
            'db_pass': 'adit',
            'db_host': 'airflow-postgres',
            'db_port': 5432,
            'db_name': 'flights_dw'
        }
    )

    extract_data >> transform_data >> load_data
