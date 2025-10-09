import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine


load_dotenv()


DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DB_URL)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
FILE_PATH = os.path.join(BASE_DIR, "ml", "data", "processed", "swing_trading_model_data.parquet")

# Load data
df = pd.read_parquet(FILE_PATH)


df.to_sql(
    name="stock_data",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Data loaded successfully into 'stock_data' table.")
