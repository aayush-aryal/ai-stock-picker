from fastapi import APIRouter, Depends
from ..models.DTOs.requests import AddStockRequest,RemoveStockRequest
from ..auth.dependencies import get_current_user
from ..services.user_stocks import user_buy_stock, user_sell_stocks, get_all_user_stocks, get_specific_stock, get_portfolio_table
from ..db import get_db

router=APIRouter(prefix="/user-owned-stocks", tags=["user-owned-stocks"])

@router.post('/buy')
async def add_user_owned_stocks(req:AddStockRequest,user=Depends(get_current_user), db=Depends(get_db)):
    response=user_buy_stock(req,db,user)
    return response

@router.post('/sell')
async def sell_user_owned_stocks(req:RemoveStockRequest, db=Depends(get_db), user=Depends(get_current_user)):
    response=user_sell_stocks(req,db,user)
    return response


@router.get('/get-stocks')
async def get_all_user_owned_stocks(db=Depends(get_db),user=Depends(get_current_user)):
    response= get_all_user_stocks(db,user)
    return response

@router.get('/get-stock')
async def get_users_specific_stock(ticker:str,db=Depends(get_db),user=Depends(get_current_user)):
    response= get_specific_stock(ticker,db,user)
    return response


@router.get("/get-portfolio")
async def get_portfolio(user=Depends(get_current_user), db=Depends(get_db)):
    response=get_portfolio_table(db,user)
    return response