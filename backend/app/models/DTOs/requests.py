from pydantic import BaseModel 
from enum import Enum
from typing import Optional
from dataclasses import dataclass

class SourceEnum(str,Enum):
    earnings_call="earnings_call"
    news="news"
class StockDataRequest(BaseModel):
    ticker:str
    start_date:str 
    end_date:Optional[str]=None

class StockDataResponse(BaseModel):
    ticker:str 
    open:str 
    close:str 
    volume:str 
    high:str 
    low:str

class PredictStockRank(BaseModel):
    ticker:str 
    date:str

class AskRagRequest(BaseModel):
    ticker:str
    query:str
    source:str
    quarter:Optional[str]=None 
    year:Optional[str]=None

@dataclass
class Context:
    source:str
    ticker:str
    quarter:Optional[str]=None 
    year:Optional[str]=None


class AddStockRequest(BaseModel):
    ticker:str 
    date:str
    amount:int 
    stockname:str

class RemoveStockRequest(BaseModel):
    ticker:str 
    date: str 
    share:float 
    