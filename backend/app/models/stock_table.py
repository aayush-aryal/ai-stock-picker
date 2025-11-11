from sqlalchemy import Column, String, Date, Float, Integer, Boolean
from sqlalchemy.orm import declarative_base
from ..db import Base


class StockData(Base):
    __tablename__ = "stock_data"

    # Primary key
    Ticker = Column(String, primary_key=True)
    Date = Column(Date, primary_key=True)

    # Raw OHLCV
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    Volume = Column(Float)

    # SP500 columns
    sp500_Open = Column(Float)
    sp500_High = Column(Float)
    sp500_Low = Column(Float)
    sp500_Close = Column(Float)
    sp500_Volume = Column(Float)

    # Engineered features
    return_5d = Column(Float)
    rsi_14d = Column(Float)
    daily_return = Column(Float)
    volatility_10d = Column(Float)
    volatility_20d = Column(Float)
    sp500_return_5d = Column(Float)
    relative_strength_5d = Column(Float)
    macd_histogram = Column(Float)
    ema_8d = Column(Float)
    ema_21d = Column(Float)
    ema_8_21_cross = Column(Integer)
    stochastic_k = Column(Float)
    stochastic_d = Column(Float)
    bollinger_percent_b = Column(Float)
    roc_21d = Column(Float)
    obv_scaled = Column(Float)
    atr_14d = Column(Float)

    # Targets
    target_5d = Column(Float)
    target_regression = Column(Float)
    target_binary = Column(Boolean)



