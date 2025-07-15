import pandas as pd


def extract_etl(
    input_file,
    output_file,
    batch_number,
    batch_size=5000
):
    skip_rows = 1 + (batch_number - 1) * batch_size
    df = pd.read_csv(
        input_file,
        skiprows=range(1, skip_rows),
        nrows=batch_size
    )
    df.to_csv(output_file, index=False)
    print(f"Extracted batch {batch_number} to {output_file}")
