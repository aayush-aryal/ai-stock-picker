from ..models.stock_table import StockData
from sqlalchemy.orm import Session
from ..models.DTOs.requests import AddStockRequest, RemoveStockRequest
from ..models.users_table import Users,UserStocks
from fastapi import HTTPException, status
from ..models.DTOs.users import UserDTO
from ..models.users_table import Transanctions,Activity
import pandas as pd
from decimal import Decimal

def user_buy_stock(request:AddStockRequest, db:Session, user):
    #get the latest stock data assume the stock table we have is always updated
    if not request.date:
        last_date=db.query(StockData.Date).order_by(StockData.Date.desc()).first()
        if last_date:
            last_date=last_date._asdict()
            request.date=last_date["Date"]
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
       total_shares=number_of_shares+ float(user_owned_stock.shares) # type: ignore
       user_owned_stock.date=request.date #type: ignore
       user_owned_stock.avg_buy_price = ((Decimal(user_owned_stock.shares) * Decimal(user_owned_stock.avg_buy_price) +Decimal(number_of_shares) * Decimal(stock.Close))/ Decimal(total_shares) # type: ignore
) # type: ignore

    else:
        #add the row to the table?
        #im thinking of just adding a row and then later maybe get history or final but this seems better for now
        user_owned_stock=UserStocks(username=user.username,
                         date=request.date,
                         stock=request.ticker,
                         shares=number_of_shares,
                         avg_buy_price=stock.Close
                         )
        db.add(user_owned_stock)
    #transanction table time
    new_transanction=Transanctions(
        username=user.username,
        stock=stock.Ticker,
        shares=number_of_shares,
        activity=Activity.buy,
        date=request.date
    )
    db.add(new_transanction)
    db_user.total_capital=db_user.total_capital-request.amount # type: ignore
    db.commit()
    db.refresh(db_user)
    db.refresh(new_transanction)
    return {"message":"Stock updated successfully", "shares":user_owned_stock.shares}


def user_sell_stocks(request:RemoveStockRequest, db:Session, user:UserDTO):

    #for date get last date in the db
    if not request.date:
        last_date=db.query(StockData.Date).order_by(StockData.Date.desc()).first()
        if last_date:
            last_date=last_date._asdict()
            request.date=last_date["Date"]
     
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

    #get the current user from db 
    user_db=db.query(Users).filter(Users.username==user.username).first()
    user_db.total_capital+=sold_price # type: ignore
    if stock_to_sell.shares==0: # type: ignore
        db.delete(stock_to_sell)
    new_transanction=Transanctions(
        username=user.username,
        stock=stock.Ticker,
        shares=request.share,
        activity=Activity.sell,
        date=request.date
    )
    db.add(new_transanction)
    db.commit()
    db.refresh(user_db)
    db.refresh(stock_to_sell)
    db.refresh(new_transanction)

    user.total_capital=user_db.total_capital # type: ignore
    
    return {"message":"Stock sold successfully","user":user,"sold_price":sold_price, "stock":stock_to_sell}



def get_all_user_stocks(db:Session, user:UserDTO):
    stocks=db.query(UserStocks).filter(UserStocks.username==user.username).all()
    res=[]
    for stock in stocks:
        latest_stock = db.query(StockData).filter(StockData.Ticker==stock.stock).order_by(StockData.Date.desc()).first()
        
        stock_dict = {
            "id": stock.id,
            "username": stock.username,
            "date": stock.date,
            "stock": stock.stock,
            "shares": float(stock.shares), # type: ignore
            "avg_buy_price": float(stock.avg_buy_price), # type: ignore
        }
        
        if latest_stock and stock.avg_buy_price:
            price_difference = float(latest_stock.Close) - stock_dict["avg_buy_price"]
            gain_loss = price_difference * stock_dict["shares"]
            gain_loss_perc = (price_difference / stock_dict["avg_buy_price"]) * 100
            
            stock_dict["gain_loss"] = gain_loss
            stock_dict["gain_loss_pct"] = gain_loss_perc
            stock_dict["latest_close"] = float(latest_stock.Close)
        else:
            stock_dict["gain_loss"] = 0 
            stock_dict["gain_loss_pct"] = 0
            stock_dict["latest_close"] = 0
        
        res.append(stock_dict)
    return {
        "username":user.username,
        "stocks":res
    }


def get_portfolio_table(db: Session, user: UserDTO):
    # 1. Fetch transactions
    transactions = db.query(
        Transanctions.date,
        Transanctions.stock,
        Transanctions.shares,
        Transanctions.activity
    ).filter(Transanctions.username == user.username).order_by(Transanctions.date.asc()).all()

    if not transactions:
        return []

    # 2. Convert to DataFrame
    tx_df = pd.DataFrame(transactions, columns=['date', 'ticker', 'shares', 'activity'])
    tx_df["shares"]=pd.to_numeric(tx_df["shares"], errors="coerce")

    tx_df['signed_shares'] = tx_df.apply(lambda row: float(row.shares) if row.activity == Activity.buy else -float(row.shares), axis=1)

   
  
    earliest_date=tx_df.iloc[0].date
    unique_tickers=tx_df['ticker'].to_list()
    
    stock_table=db.query(StockData.Ticker,
                         StockData.Close,
                         StockData.Date).filter(StockData.Ticker.in_(unique_tickers),
                                                 StockData.Date>=earliest_date).all()
    
    stock_table_df=pd.DataFrame(stock_table, columns=["ticker","close","date"])
    merged_df=stock_table_df.merge(tx_df, how="left", on=["ticker","date"])
    merged_df["date"]=pd.to_datetime(merged_df["date"])
    merged_df=merged_df.sort_values("date")
    merged_df=merged_df.drop(columns="activity")
    merged_df=merged_df.fillna(0)

    
    
    merged_df["signed_shares"] = merged_df.groupby("ticker")["signed_shares"].cumsum()
    merged_df["daily_value"]=merged_df["signed_shares"]*merged_df["close"]


    latest_positions = merged_df.groupby(['date', 'ticker']).tail(1)

    portfolio_df = latest_positions.groupby("date")["daily_value"].sum().reset_index()
    portfolio_df.columns = ["date", "portfolio_value"]
    return portfolio_df.to_dict(orient="records")

    

def get_specific_stock(ticker:str,db:Session, user:UserDTO):
    stocks=db.query(UserStocks).filter(UserStocks.stock==ticker,
                                       UserStocks.username==user.username).first()
    gain_loss=0
    gain_loss_perc=0
    if stocks:
        latest_stock=db.query(StockData).filter(StockData.Ticker==stocks.stock).order_by(StockData.Date.desc()).first()
        gain_loss=(latest_stock.Close-float(stocks.avg_buy_price))*float(stocks.shares) if latest_stock else 0 # type: ignore
        gain_loss_perc=((latest_stock.Close-float(stocks.avg_buy_price)) /float(stocks.avg_buy_price))*100 if latest_stock else 0 # type: ignore

    return {
        "stock":stocks,
         "user":user,
         "gain_loss":gain_loss,
         "gain_loss_perc":gain_loss_perc
    }



