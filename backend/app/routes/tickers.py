from fastapi import APIRouter
from ..services.ticker_info import get_financial_income_statement, get_earning_call_transcripts, get_ticker_news, ask_rag, get_ticker_info
from fastapi import Depends, Request
from ..models.DTOs.requests import  AskRagRequest, Context




def get_agent(request:Request):
    return request.app.state.agent
router=APIRouter(prefix='/ticker', tags=['ticker'])


@router.get("/get-income-statement")
async def get_income_satement(ticker:str):
    income_statement= await get_financial_income_statement(ticker)
    return {
        'ticker':ticker,
        'statement':income_statement
    }


@router.get('/get-earning-call-transcript')
async def get_earning_call_transcript(ticker:str, year:int, quarter:int):
    transcripts= await get_earning_call_transcripts(ticker,year,quarter)
    return {
        'ticker':ticker,
        'transcript':transcripts
    }


@router.get('/get-ticker-news')
async def get_ticker_news_(ticker:str):
    news=await get_ticker_news(ticker)
    return {
        'ticker':ticker,
        'news':news
    }


@router.get('/get-ticker-info')
async def get_ticker_information(ticker:str):
    info=await get_ticker_info(ticker)
    return {
        'ticker':ticker,
        'info':info
    }



@router.post('/rag')
async def ask_rag_(request:AskRagRequest, agent=Depends(get_agent)):
    context=Context(source=request.source, ticker=request.ticker,quarter=request.quarter, year=request.year)
    response=await ask_rag(agent,context,request.query)
    return {
        'ticker':request.ticker,
        'llm_response':response
    }

