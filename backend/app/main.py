from fastapi import FastAPI,Depends
from .models.requests import StockDataRequest,PredictStockRank
from .services.stock_data import get_stock_data,update_db
from .services.model_llm import predict_rank,get_top_15_stocks_for_day
from .db import get_db
from sqlalchemy.orm import Session

app=FastAPI()

@app.get("/")
async def root():
    return {"message":"hello world",
            }

@app.post("/get-stock-prediction")
async def get_stock_prediction(request:StockDataRequest):
    return {"data":request.ticker}

@app.post('/get-stock-data')
async def fetch_stock_data(request:StockDataRequest, db:Session=Depends(get_db)):
    data=get_stock_data(db=db,request=request)
    return data

@app.post('/update-stock-data')
async def update_stock_data(end_date, db:Session=Depends(get_db)):
    result=update_db(db=db, end_date=end_date)
    return {"status":result}

@app.post('/predict-stock')
async def predict_stock(request:PredictStockRank, db:Session=Depends(get_db)):
    prediction=predict_rank(db,request)
    return {"prediction":prediction}

@app.post('/get-top-15')
async def get_top_15(date,db:Session=Depends(get_db)):
    prediction=get_top_15_stocks_for_day(db=db,date=date)
    return {
        "date":date,
        "prediction":prediction
    }
    


