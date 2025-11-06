import numpy as np
import pandas as pd
import yfinance as yf
import requests
import io

#transformation function to use user query

def normalize_ticker(ticker):
    return ticker.replace(".","-")

def list_slickcharts_sp500():
    url = 'https://www.slickcharts.com/sp500'
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0'  # Default user-agent fails.
    response = requests.get(url, headers={'User-Agent': user_agent})
    ticker= pd.read_html(io.StringIO(response.text), match='Symbol', index_col='Symbol')[0] # type: ignore
    ticker=ticker.reset_index()
    symbols=ticker["Symbol"].tolist()
    symbols=[normalize_ticker(tick) for tick in symbols]
    return symbols

def get_stock_market_data(start_date,end_date, tickers=None):
    if not tickers:
        tickers= list_slickcharts_sp500()    
    data = yf.download(tickers, start=start_date, end=end_date, 
                      group_by='ticker', auto_adjust=True)
    
    data=data.stack(level=0).reset_index() # type: ignore
    return data




def calculate_rsi(prices,window=14):
    """Calculate RSI - momentum oscillator measuring speed of price movements"""
    delta=prices.diff()
    gain=(delta.where(delta>0,0)).rolling(window=window).mean()
    loss=(-delta.where(delta<0,0)).rolling(window=window).mean()

    rs=gain/loss
    rsi=100-(100/(1+rs))
    return rsi 
  

def feature_engineer(df):
    df_copy=df.copy()
    df_copy=df_copy.sort_values(by=["Ticker","Date"])
    #return for 5d would be 
    df_copy['return_5d'] = df_copy.groupby("Ticker")["Close"].transform(
        lambda x: (x.shift(1)/x.shift(6)-1)
    )
    #rsi 
    df_copy['rsi_14d']=df_copy.groupby("Ticker")["Close"].transform(
        lambda x:calculate_rsi(x).shift(1)
    )
    

    #volatility 
    #how much a stock goes up or down per time or its movement? check daily return see how it much it has fluctuated
    df_copy['daily_return'] = df_copy.groupby('Ticker')['Close'].pct_change().shift(1)
    df_copy["volatility_10d"]=df_copy.groupby("Ticker")["daily_return"].transform(
        lambda x:x.rolling(window=10).std()
    )
    df_copy["volatility_20d"]=df_copy.groupby("Ticker")["daily_return"].transform(
        lambda x:x.rolling(window=20).std()
    )

    #market 5d percentage return
    df_copy["sp500_return_5d"]=(df_copy["sp500_Close"].shift(1)/df_copy["sp500_Close"].shift(6)-1)

    #relative strength
    df_copy['relative_strength_5d']=df_copy['return_5d']-df_copy['sp500_return_5d']

    #more trend based signals 
    ema_12 = df_copy.groupby('Ticker')['Close'].transform(lambda x: x.ewm(span=12).mean())
    ema_26 = df_copy.groupby('Ticker')['Close'].transform(lambda x: x.ewm(span=26).mean())
    macd = ema_12 - ema_26
    df_copy['macd']=macd
    macd_signal = df_copy.groupby('Ticker')['macd'].transform(lambda x: x.ewm(span=9).mean())
    macd_histogram = macd - macd_signal
    df_copy['macd_histogram'] = macd_histogram.shift(1)

    # Shift all final feature avoid collinearity
    df_copy=df_copy.drop(columns=['macd'])

    df_copy['ema_8d']=df_copy.groupby("Ticker")["Close"].transform(lambda x: x.ewm(span=8).mean()).shift(1)

    df_copy['ema_21d']=df_copy.groupby("Ticker")["Close"].transform(lambda x: x.ewm(span=21).mean()).shift(1)

    df_copy['ema_8_21_cross'] = (df_copy['ema_8d'] > df_copy['ema_21d']).astype(int)

    #stochastic oscillator
    low_14 = df_copy.groupby('Ticker')['Low'].transform(lambda x: x.rolling(14, min_periods=14).min())
    high_14 = df_copy.groupby('Ticker')['High'].transform(lambda x: x.rolling(14, min_periods=14).max())
    df_copy['stochastic_k']=100*((df_copy["Close"]-low_14)/(high_14-low_14)).shift(1)
    df_copy['stochastic_d'] = df_copy.groupby('Ticker')['stochastic_k'].transform(lambda x: x.rolling(3).mean()).shift(1)

    #bollinger band
    sma_20 = df_copy.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=20).mean())
    std_20 = df_copy.groupby('Ticker')['Close'].transform(lambda x: x.rolling(window=20).std())
    upper_band = sma_20 + (2 * std_20)
    lower_band = sma_20 - (2 * std_20)
    df_copy['bollinger_percent_b'] = ((df_copy['Close'] - lower_band) / (upper_band - lower_band)).shift(1)

    #roc
    #the percentage change in price between the current price and the price n periods ago. It's a pure momentum oscillator.
    df_copy['roc_21d'] = df_copy.groupby("Ticker")["Close"].transform(
    lambda x: (x / x.shift(21) - 1)
    ).shift(1)

    #obv 
    direction = df_copy.groupby('Ticker')['Close'].transform(lambda x: x.diff()).fillna(0).apply(np.sign)
    obv = (df_copy['Volume'] * direction).groupby(df_copy['Ticker']).cumsum()
    df_copy['obv_scaled'] = obv.groupby(df_copy['Ticker']).transform(
        lambda x: (x - x.rolling(window=21).mean()) / x.rolling(window=21).std()
    ).shift(1)


    #atr 
    high_low=df_copy['High']- df_copy['Low']
    high_close=np.abs(df_copy['High']-df_copy.groupby("Ticker")['Close'].shift(1))
    low_close=np.abs(df_copy['Low']-df_copy.groupby("Ticker")["Close"].shift(1))
    tr=pd.concat([high_low,high_close,low_close], axis=1).max(axis=1)
    df_copy['atr_14d']=tr.groupby(df_copy['Ticker']).transform(
        lambda x:x.ewm(span=14, adjust=False).mean()
    ).shift(1)

    
    df_copy = df_copy.replace([np.inf, -np.inf], np.nan)
    return df_copy


def target_engineer(df):
    #target
    df_copy=df.copy()
    df_copy["target_5d"]=df_copy.groupby("Ticker")["Close"].transform(
        lambda x:(x.shift(-5)/x-1)
    )

    return df_copy


# Fetch SP500 index data for the same time period
def get_sp500_index_data(start_date,end_date):
    print("Fetching SP500 index data...")
    sp500_data = yf.download("^GSPC", start=start_date, end=end_date, auto_adjust=True, group_by='Ticker')
    sp500_data=sp500_data.stack(level=0).reset_index() # type: ignore
    sp500_data=sp500_data.drop(columns=["Ticker"])

    
    # Rename columns to avoid conflicts
    sp500_data.columns = ['Date', 'sp500_Open', 'sp500_High', 'sp500_Low', 
                         'sp500_Close', 'sp500_Volume']
   
    return sp500_data

