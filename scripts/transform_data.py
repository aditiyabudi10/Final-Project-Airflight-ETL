import pandas as pd


def transform_etl(input_file, output_file):
    df = pd.read_csv(input_file)

    print(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Columns found: {df.columns.tolist()}")

    # pastikan kolom yang relevan ada
    required_cols = ['UniqueCarrier', 'DepDelay', 'ArrDelay']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Kolom berikut tidak ditemukan di CSV: {missing_cols}")

    # hanya kolom yang relevan
    df = df[required_cols]

    # bersihkan data: drop baris dengan NA di kolom penting
    before = len(df)
    df = df.dropna(subset=['DepDelay', 'ArrDelay'])
    after = len(df)
    print(f"Dropped {before - after} rows with missing DepDelay or ArrDelay.")

    if 'DepTime' in df.columns:
        df['TimeOfDay'] = pd.cut(
            df['DepTime'],
            bins=[0, 600, 1200, 1800, 2400],
            labels=['Night', 'Morning', 'Afternoon', 'Evening']
            )
    else:
        print("Kolom DepTime tidak ditemukan, TimeOfDay dilewati.")

    # Hitung rata-rata delay per maskapai
    summary = (
        df.groupby('UniqueCarrier')
          .agg({'DepDelay': 'mean', 'ArrDelay': 'mean'})
          .reset_index()
    )

    summary.columns = ['UniqueCarrier', 'AVG_DEP_DELAY', 'AVG_ARR_DELAY']

    summary.to_parquet(output_file, index=False)
    print(f"Transformed data saved to: {output_file}")


if __name__ == "__main__":
    transform_etl(
        input_file='/opt/airflow/data/hflights.csv',
        output_file='/opt/airflow/data/hflights_transformed.parquet'
    )
