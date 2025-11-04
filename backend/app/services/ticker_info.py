from defeatbeta_api.data.ticker import Ticker
from ..utils.clean_np import clean_for_sqlalchemy
from ..utils.rag_helpers import ask_agent, add_news_to_vector_store, add_earning_call_to_vector_store
from typing import Optional

async def get_financial_income_statement(ticker_name:str):
    ticker=Ticker(ticker_name)
    statement=ticker.quarterly_income_statement().df()
    statement=statement.to_dict('records')
    organized_data = {
    record['Breakdown']: {
        key: value for key, value in record.items() if key != 'Breakdown'
    }
    for record in statement
}       
    return organized_data


async def get_earning_call_transcripts(ticker_name:str, year:int, quarter:int):
    ticker=Ticker(ticker_name)
    transcript=ticker.earning_call_transcripts()
    transcript=transcript.get_transcript(year,quarter)
    transcript=transcript.to_dict('records')
    add_earning_call_to_vector_store(transcript,year,quarter,ticker_name)
    return transcript


async def get_ticker_news(ticker_name:str):
    ticker=Ticker(ticker_name)
    news=ticker.news().get_news_list()
    news= news.to_dict('records')
    print(len(news))
    news=clean_for_sqlalchemy(news[:5])
    #add news to vector store
    add_news_to_vector_store(news,ticker_name)
    return news


async def ask_rag(agent,context,query:str):
    response=await ask_agent(agent,f"{query}",context)
    return response



async def get_ticker_info(ticker_:str):
    ticker=Ticker(ticker_)
    info=ticker.info().to_dict('records')
    info=clean_for_sqlalchemy(info)
    print(info)
    return info
