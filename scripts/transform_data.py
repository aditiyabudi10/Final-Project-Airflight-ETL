import pandas as pd


def transform_etl(input_file, output_file_summary, output_file_full):

    # gabungkan semua file CSV
    df_list = []
    for file in input_file:
        df = pd.read_csv(file)
        df_list.append(df)
    combined_df = pd.concat(df_list, ignore_index=True)
    print(f'total rows after combining: {len(combined_df)}')

    # pastikan kolom yang relevan ada
    required_cols = ['UniqueCarrier', 'DepDelay', 'ArrDelay']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        raise KeyError(f"Kolom berikut tidak ditemukan di CSV: {missing_cols}")

    # hanya kolom yang relevan
    df = combined_df[required_cols + (['DepTime'] if 'DepTime' in combined_df
                                      .columns else 'Tidak ada kolom DepTime')]

    # bersihkan data: drop baris dengan NA di kolom penting
    before = len(df)
    df = df.dropna(subset=['DepDelay', 'ArrDelay'])
    after = len(df)
    print(f"Dropped {before - after} rows with missing DepDelay or ArrDelay.")

    # ubah DepTime menjadi kategori waktu
    if 'DepTime' in df.columns:
        df['TimeOfDay'] = pd.cut(
            df['DepTime'],
            bins=[0, 600, 1200, 1800, 2400],
            labels=['Night', 'Morning', 'Afternoon', 'Evening']
            )
    else:
        print("Kolom DepTime tidak ditemukan, TimeOfDay dilewati.")

    print(f"Transformed data shape: {df}")

    # simpan hasil kategori waktu ke file parquet
    df.to_parquet(output_file_full, index=False)
    print(f"Transformed data saved to: {output_file_full}")

    # Hitung rata-rata delay per maskapai
    summary = (
        df.groupby('UniqueCarrier')
          .agg({'DepDelay': 'mean', 'ArrDelay': 'mean'})
          .reset_index()
    )

    summary.columns = ['UniqueCarrier', 'AVG_DEP_DELAY', 'AVG_ARR_DELAY']

    # menyimpan hasil transformasi summary ke file parquet
    summary.to_parquet(output_file_summary, index=False)
    print(f"Transformed data saved to: {output_file_summary}")


if __name__ == "__main__":
    transform_etl(
        input_file='/opt/airflow/data/hflights.csv',
        output_file_summary=(
            '/opt/airflow/data/output/hflights_summary.parquet'
        ),
        output_file_full=(
            '/opt/airflow/data/output/hflights_day.parquet'
        ),
    )
