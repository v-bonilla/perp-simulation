import os

import pandas as pd


def create_test_feather_files(
    original_file_path: str,
    new_file_path: str,
    date_column: str,
    from_ts: str,
    to_ts: str,
):
    # Load the original file
    df = pd.read_feather(original_file_path)
    # Filter the data
    df = df[(df[date_column] >= from_ts) & (df[date_column] < to_ts)].copy()
    df.reset_index(drop=True, inplace=True)
    # Save the new file
    if not os.path.exists(new_file_path):
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        df.to_feather(new_file_path)
