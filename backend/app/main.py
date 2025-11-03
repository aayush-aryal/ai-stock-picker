from fastapi import FastAPI,Depends
from .models.requests import StockDataRequest,PredictStockRank, AskRagRequest, Context
from .services.stock_data import get_stock_data,update_db
from .services.model_llm import predict_rank,get_top_15_stocks_for_day
from .services.ticker_info import get_financial_income_statement, get_earning_call_transcripts, get_ticker_news, ask_rag
from .db import get_db
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from .utils.rag_helpers import initialize_rag_system
from fastapi import Depends,Request
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional





@asynccontextmanager
async def lifespan(app:FastAPI):
    # instantiate vector store and agent
    agent=initialize_rag_system()
    app.state.agent=agent
    yield 

def get_agent(request:Request):
    return request.app.state.agent

app=FastAPI(lifespan=lifespan)
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="token")



#authentication flow



#endpoints

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
    
@app.get("/get-income-statement")
async def get_income_satement(ticker:str):
    income_statement= await get_financial_income_statement(ticker)
    return {
        'ticker':ticker,
        'statement':income_statement
    }


@app.get('/get-earning-call-transcript')
async def get_earning_call_transcript(ticker:str, year:int, quarter:int):
    transcripts= await get_earning_call_transcripts(ticker,year,quarter)
    return {
        'ticker':ticker,
        'transcript':transcripts
    }


@app.get('/get-ticker-news')
async def get_ticker_news_(ticker:str):
    news=await get_ticker_news(ticker)
    return {
        'ticker':ticker,
        'news':news
    }


@app.post('/rag')
async def ask_rag_(request:AskRagRequest, agent=Depends(get_agent)):
    context=Context(source=request.source, ticker=request.ticker,quarter=request.quarter, year=request.year)
    response=await ask_rag(agent,context,request.query)
    return {
        'ticker':request.ticker,
        'llm_response':response
    }

@app.get("/items")
async def read_items(token:Annotated[str,Depends(oauth2_scheme)]):
    return{"token":token}