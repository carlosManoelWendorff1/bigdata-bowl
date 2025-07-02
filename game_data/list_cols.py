import pandas as pd

# Caminho para seu arquivo Parquet
parquet_path = "./tracking_week_1.parquet"

# Carrega o arquivo Parquet
try:
    df = pd.read_parquet(parquet_path, engine = "fastparquet")
    print("Colunas disponíveis:")
    print(df.dtypes)
except Exception as e:
    print(f"Erro ao carregar o arquivo Parquet:\n{e}")