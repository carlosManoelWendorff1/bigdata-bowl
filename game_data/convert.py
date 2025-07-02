import pandas as pd

def csv_to_parquet(csv_file_path, parquet_file_path):
    df = pd.read_csv(csv_file_path)

    df.to_parquet(parquet_file_path, index=False)

    print(f"Arquivo convertido com sucesso: {parquet_file_path}")

if __name__ == "__main__":
    csv_file = "tracking_week_1.csv"        
    parquet_file = "tracking_week_1.parquet"
    csv_to_parquet(csv_file, parquet_file)