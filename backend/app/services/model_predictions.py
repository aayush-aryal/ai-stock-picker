import os 
import joblib
from sqlalchemy.orm import Session
from ..models.requests import PredictStockRank
from ..models.stock_table import StockData
import pandas as pd
from ..core.config import settings
import numpy as np

BASE_DIR=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "models", "xgbranker_base.pkl")


MODEL=joblib.load(MODEL_PATH)


def predict_rank(db: Session, request: PredictStockRank):
    date = request.date
    ticker = request.ticker

    # Fetch stock data for that date
    stock_day = db.query(StockData).filter(
        StockData.Date == request.date,
    ).all()

    if not stock_day:
        return {"error": f"No data found for {ticker} on {date}"}

    df = pd.DataFrame([row.__dict__ for row in stock_day])
    df.drop(columns=["_sa_instance_state"], inplace=True, errors="ignore")
    X = df[settings.FEATURE_COLS]
    df["score"] = MODEL.predict(X)

    # percentile directly as 0–100
    df["percentile"] = df["score"].rank(pct=True) * 100

    # pick your ticker
    ticker_row = df[df["Ticker"] == ticker].iloc[0]
    percentile = float(ticker_row["percentile"])
    score = float(ticker_row["score"])


    return {
        "ticker": ticker,
        "date": date,
        "score": score,
        "percentile_rank": percentile,
        "message": f"{ticker} is in the top {round(percentile, 2)}% performers for {date}",
    }

    

def get_top_15_stocks_for_day(db: Session, date: str):
    stock_day = db.query(StockData).filter(StockData.Date == date).all()
    if not stock_day:
        return {"message":f"Could not get predicitions for {date} "}
    df = pd.DataFrame([row.__dict__ for row in stock_day])
    df.drop(columns=["_sa_instance_state"], inplace=True, errors="ignore")

    X = df[settings.FEATURE_COLS]
    df['score'] = MODEL.predict(X)
    df['percentile'] = df['score'].rank(pct=True) * 100

    top15 = df.nlargest(15, 'score')

    # Convert to dict and return
    return top15.to_dict(orient='records')

    



    








    


