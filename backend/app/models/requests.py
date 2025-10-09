from pydantic import BaseModel 

class StockDataRequest(BaseModel):
    ticker:str
    start_date:str 
    end_date:str

class PredictStockRank(BaseModel):
    ticker:str 
    date:str

