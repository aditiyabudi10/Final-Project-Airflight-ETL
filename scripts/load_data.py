import pandas as pd
from sqlalchemy import create_engine


def load_etl(input_file,
             input_file_day,
             table_name,
             table_name_full,
             db_user='postgres',
             db_pass='adit',
             db_host='airflow-postgres',
             db_port=5432,
             db_name='flights_dw'):
    """
    Load parquet file to PostgreSQL.
        """
    # Baca file parquet
    df = pd.read_parquet(input_file)
    df2 = pd.read_parquet(input_file_day)

    # Buat koneksi SQLAlchemy
    connection_uri = (
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    engine = create_engine(connection_uri)

    # Load ke PostgreSQL
    with engine.begin() as connection:
        df.to_sql(table_name,
                  connection,
                  if_exists='replace',
                  index=False)

    print(f"Data loaded to PostgreSQL table {table_name}")

    with engine.begin() as connection:
        df2.to_sql(
            table_name_full,
            connection,
            if_exists='replace',
            index=False
        )

    print(f"Data loaded to PostgreSQL table {table_name_full}")


if __name__ == "__main__":
    load_etl(
        input_file='/opt/airflow/data/output/hflights_summary.parquet',
        table_name='flights_summary'
    )
    load_etl(
        input_file='/opt/airflow/data/output/hflights_day.parquet',
        table_name_full='flights_full'
    )
