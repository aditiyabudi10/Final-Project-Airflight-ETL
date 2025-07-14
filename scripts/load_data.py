import pandas as pd
from sqlalchemy import create_engine


def load_etl(input_file,
             table_name,
             db_user='postgres',
             db_pass='adit',
             db_host='airflow-postgres',
             db_port=5432,
             db_name='flights_dw'):
    """
    Load parquet file to PostgreSQL.

    Args:
        input_file (str): path to parquet file
        table_name (str): target table in PostgreSQL
        db_user (str): database username (root)
        db_pass (str): database password (dibimbing)
        db_host (str): database host (airflow-postgres)
        db_port (int): database port (5432)
        db_name (str): database name (flights_dw)
    """
    # Baca file parquet
    df = pd.read_parquet(input_file)

    # Buat koneksi SQLAlchemy
    connection_uri = (
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )
    engine = create_engine(connection_uri)

    # Load ke PostgreSQL
    with engine.begin() as connection:
        df.to_sql(table_name, connection, if_exists='append', index=False)

    print(f"Data loaded to PostgreSQL table {table_name}")
