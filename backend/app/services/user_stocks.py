from ..models.stock_table import StockData
from sqlalchemy.orm import Session
from ..models.DTOs.requests import AddStockRequest, RemoveStockRequest
from ..models.users_table import Users,UserStocks
from fastapi import HTTPException, status
import yfinance as yf

def user_buy_stock(request:AddStockRequest, db:Session, user):
    #get the latest stock data assume the stock table we have is always updated
    stock=db.query(StockData).filter(StockData.Date==request.date,
                                     StockData.Ticker==request.ticker).first()
    #check if the stock is already present in the db
    #doesnt add a new row adds to stock if present
    user_owned_stock=db.query(UserStocks).filter(UserStocks.username==user.username,
                                                 UserStocks.stock==request.ticker).first()
    if not stock or not user:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,"Could not add the stock")
    number_of_shares=request.amount/ stock.Close
    db_user=db.query(Users).filter(Users.username==user.username).first()
    if user_owned_stock:
        
        user_owned_stock.shares+=number_of_shares # type: ignore
        user_owned_stock.date=request.date #type: ignore
    else:
        #add the row to the table?
        #im thinking of just adding a row and then later maybe get history or final but this seems better for now
        stock=UserStocks(username=user.username,
                         date=request.date,
                         stock=request.ticker,
                         shares=number_of_shares
                         )
        db.add(stock)

    db_user.total_capital=db_user.total_capital-request.amount # type: ignore
    db.commit()
    db.refresh(db_user)
    return {"message":"Stock updated successfully"}


def user_sell_stocks(request:RemoveStockRequest, db:Session, user):

    #get teh stock data 
    stock=db.query(StockData).filter(StockData.Ticker==request.ticker,
                                     StockData.Date== request.date
                                     ).first()
    #if usewr tries to sell unowned stock idk how ui would let it but raise exception
    stock_to_sell=db.query(UserStocks).filter(UserStocks.stock==request.ticker,
                                            UserStocks.username==user.username).first()
    if not stock_to_sell or stock_to_sell.shares<request.share or not stock: # type: ignore
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Something went wrong while attempting to sell stock")

    #if user both has the stock and more than what they currently have 
    curr_price=stock.Close
    sold_price=curr_price*request.share
    stock_to_sell.shares-=request.share # type: ignore

    #get the current suer from db 
    user_db=db.query(Users).filter(Users.username==user.username).first()
    user_db.total_capital+=sold_price # type: ignore
    if stock_to_sell.shares==0: # type: ignore
        db.delete(stock_to_sell)
    db.commit()
    db.refresh(user_db)
    db.refresh(stock_to_sell)
    return {"message":"Stock sold successfully","user":user,"sold_price":sold_price}

