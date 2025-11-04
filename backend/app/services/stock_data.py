import pandas as pd 
from ..models.DTOs.requests import StockDataRequest
from ..models.stock_table import StockData
from ..utils.feature_engineer import (feature_engineer,
                                      target_engineer,
                                    get_sp500_index_data, 
                                    get_stock_market_data)
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime,timezone,timedelta
from dateutil.parser import parse
from fastapi.encoders import jsonable_encoder
import numpy as np


def stock_data_to_dict(df:pd.DataFrame)-> list[dict]:
    if df.empty:
        return []
    return df.to_dict("records")



def get_stock_data(db:Session,request:StockDataRequest)-> list[StockData]:
    # assumption that db is updated for now
    df_ticker=db.query(StockData).filter(
        StockData.Ticker==request.ticker,
        StockData.Date>=request.start_date,
        StockData.Date<=request.end_date
    ).all()
    data = jsonable_encoder(df_ticker) 
    return data



def merge_and_process(df1,df2)-> pd.DataFrame:
    merged=pd.merge(df1,df2,how="left",on="Date")
    engineered=feature_engineer(merged)
    return engineered

def get_data(start,end)->pd.DataFrame:
    df_stocks=get_stock_market_data(start,end)
    df_market=get_sp500_index_data(start,end)
    df_final=merge_and_process(df_stocks,df_market)
    return df_final


def update_db(db: Session, end_date: str) -> str:
    try:

        last_date = db.query(func.max(StockData.Date)).scalar()
        if not last_date:
            return "Database empty or unsupported ticker"
        last_date = last_date.replace(tzinfo=timezone.utc)


        end_date_dt = parse(end_date).replace(tzinfo=timezone.utc)
        fetch_end = min(end_date_dt, datetime.now(timezone.utc) - timedelta(days=1))

        if last_date >= fetch_end:
            return "Database up to date"


        lookback = 35
        fetch_start = last_date - timedelta(days=lookback)
        df = get_data(fetch_start, fetch_end)
        print(df.shape)

        df = df[(df['Date'] >=fetch_start.replace(tzinfo=None))& (df["Date"]<=fetch_end.replace(tzinfo=None))]
        print(df.shape)
        if df.empty:
            return "No new data to insert"

        df = feature_engineer(df)
        df = target_engineer(df)
        feature_cols = [
            'return_5d', 'rsi_14d', 'volatility_10d', 'volatility_20d', 
            'sp500_return_5d', 'relative_strength_5d', 'ema_8d', 'ema_21d', 
            'ema_8_21_cross', 'stochastic_k', 'stochastic_d', 'bollinger_percent_b', 
            'roc_21d', 'obv_scaled', 'atr_14d', 'macd_histogram'
                ]

        # Only drop rows where **features are NaN**, keep rows with NaN targets
        df = df.dropna(subset=feature_cols)
        df=df.replace([np.nan,np.inf,-np.inf],None)
    # Keep only the rows that are **after last_date**
        df_new = df[df['Date'] > last_date.replace(tzinfo=None)]
        if df_new.empty:
            return "No new data to insert"
        columns_to_save = [col for col in df_new.columns if col in StockData.__table__.columns.keys()]
        stock_objs = [StockData(**row) for row in df_new[columns_to_save].to_dict("records")]  # type: ignore
        db.bulk_save_objects(stock_objs)
        db.commit()

        return f"Data Updated successfully: {len(stock_objs)} rows inserted"

    except Exception as e:
        db.rollback()
        return f"Error occurred while updating: {e}"
