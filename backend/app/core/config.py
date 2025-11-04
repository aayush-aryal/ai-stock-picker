import os
from pydantic_settings import BaseSettings


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class Settings(BaseSettings):
    DATABASE_URL: str="postgresql://postgres:password@localhost:5432/swing-trade"
    BASE_DIR: str = BASE_DIR
    FILE_PATH: str = os.path.join(BASE_DIR, "ml", "data", "processed", "swing_trading_model_data.parquet")
    MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "models", "xgbranker_base.pkl")

    LOOKBACK_DAYS: int = 35

    FEATURE_COLS:list[str]=[
                    'return_5d', 'rsi_14d', 'volatility_10d', 'volatility_20d', 
                   'sp500_return_5d', 'relative_strength_5d',
                   "stochastic_k","stochastic_d",'ema_8_21_cross','ema_21d',
                   'ema_8d','macd_histogram','obv_scaled','atr_14d','bollinger_percent_b','roc_21d',
                ]
    SECRET_KEY:str=""
    ALGORITHM:str=""
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30

    class Config:
        env_file = ".env"

settings = Settings()
