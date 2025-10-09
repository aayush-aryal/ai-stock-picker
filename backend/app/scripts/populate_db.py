import pandas as pd
from sqlalchemy import create_engine
from ..core.config import settings


engine = create_engine(settings.DATABASE_URL)
df = pd.read_parquet(settings.FILE_PATH)


df.to_sql(
    name="stock_data",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000,
    method="multi"
)

print("Data loaded successfully into 'stock_data' table.")
