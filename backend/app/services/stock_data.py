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
from defeatbeta_api.data.ticker import Ticker


def stock_data_to_dict(df:pd.DataFrame)-> list[dict]:
    if df.empty:
        return []
    return df.to_dict("records")


def get_stock_data(db:Session,request:StockDataRequest)-> list:
    # assumption that db is updated for now
    end_date=request.end_date
    if not request.end_date:
        last_stock=db.query(StockData).filter(StockData.Ticker==request.ticker).order_by(StockData.Date.desc()).first()
        end_date=last_stock.Date if last_stock else ""
    print(end_date)
    df_ticker=db.query( StockData.Date,
        StockData.Open,
        StockData.High,
        StockData.Low,
        StockData.Close,
        StockData.Volume
).filter(
        StockData.Ticker==request.ticker,
        StockData.Date>=request.start_date,
        StockData.Date<=end_date
    ).all()
    data = [row._asdict() for row in df_ticker]
    return data

def get_day_stock_data(ticker:str,date:str,db:Session):
    stock=db.query(        StockData.Open,
        StockData.High,
        StockData.Low,
        StockData.Close,
        StockData.Volume).filter(StockData.Ticker==ticker,
                                     StockData.Date==date).first()
    
    data=stock._asdict()if stock else {}
    return data



def merge_and_process(df1,df2)-> pd.DataFrame:
    merged=pd.merge(df1,df2,how="left",on="Date")
    engineered=feature_engineer(merged)
    return engineered

def get_data(start,end,ticker=None)->pd.DataFrame:
    df_stocks=get_stock_market_data(start,end,ticker)
    df_market=get_sp500_index_data(start,end)
    df_final=merge_and_process(df_stocks,df_market)
    print("df that should be appended")
    print(df_final)
    return df_final



def update_db(db: Session, end_date: str) -> str:
    try:

        last_date = db.query(func.max(StockData.Date)).scalar()
        if not last_date:
            return "Database empty or unsupported ticker"
        # last_date = last_date.replace(tzinfo=timezone.utc)
        tickers_in_db = (
            db.query(StockData.Ticker)
            .distinct()
            .all()
        )
        end_date_dt = parse(end_date).replace(tzinfo=timezone.utc)
        fetch_end = min(end_date_dt, datetime.now(timezone.utc) - timedelta(days=1))
        last_date = datetime.combine(last_date, datetime.min.time()).replace(tzinfo=timezone.utc)
        if last_date >= fetch_end:
            return "Database up to date"
        lookback = 60
        fetch_start = last_date - timedelta(days=lookback)

        feature_cols = [
            'return_5d', 'rsi_14d', 'volatility_10d', 'volatility_20d', 
            'sp500_return_5d', 'relative_strength_5d', 'ema_8d', 'ema_21d', 
            'ema_8_21_cross', 'stochastic_k', 'stochastic_d', 'bollinger_percent_b', 
            'roc_21d', 'obv_scaled', 'atr_14d', 'macd_histogram'
                ]
        total=0
    # Keep only the rows that are **after last_date**
        tickers_in_db = [t[0] for t in tickers_in_db]
        for ticker in tickers_in_db:
            last_date_for_ticker=db.query(func.max(StockData.Date)).filter(StockData.Ticker==ticker).scalar()
            last_date_for_ticker=pd.to_datetime(last_date_for_ticker)
            df=get_data(fetch_start,end_date,ticker)
            df = feature_engineer(df)
            df = target_engineer(df)
            df = df.dropna(subset=feature_cols)
            df=df.replace([np.nan,np.inf,-np.inf],None)
            ticker_data=df[(df['Date']>last_date_for_ticker)& (df['Ticker']==ticker)].copy()
            if not ticker_data.empty:
                total+=ticker_data.shape[0]
                columns_to_save = [col for col in ticker_data.columns if col in StockData.__table__.columns.keys()]
                stock_objs = [StockData(**row) for row in ticker_data[columns_to_save].to_dict("records")]  # type: ignore
                db.bulk_save_objects(stock_objs)
        db.commit()
        return f"Data Updated successfully: {total} rows inserted"

    except Exception as e:
        db.rollback()
        return f"Error occurred while updating: {e}"
