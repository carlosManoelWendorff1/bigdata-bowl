import pandas as pd
import os

def split_parquet_by_gameid(input_file, output_dir):
    df = pd.read_parquet(input_file)

    if 'gameId' not in df.columns:
        raise ValueError("Column 'gameId' not found in input file")

    os.makedirs(output_dir, exist_ok=True)

    for game_id, group in df.groupby('gameId'):
        output_path = os.path.join(output_dir, f"game_{int(game_id)}.parquet")
        group.to_parquet(output_path, index=False)
        print(f"Saved: {output_path}")

split_parquet_by_gameid("tracking_week_1.parquet", "tracking_week_1")