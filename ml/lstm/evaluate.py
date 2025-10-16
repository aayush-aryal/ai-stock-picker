# evaluate.py
import torch
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
from torch.utils.data import TensorDataset, DataLoader
from model import LSTMModel, BidirectionalLSTM


def create_sequences(features, sequence_length):
    X = []
    for i in range(len(features) - sequence_length):
        X.append(features[i:i + sequence_length])
    return np.array(X)

def evaluate_performance(df, risk_free_rate=0.02, transaction_cost=0.001):
    strategy_returns = []
    market_returns = []
    

    df = df.sort_values('Date')
    all_dates = sorted(df['Date'].unique())
    
    # Trade every 5 days
    for i in range(0, len(all_dates), 5):
        trade_date = all_dates[i]
        day_data = df[df['Date'] == trade_date]
        if len(day_data) < 15:
            continue
        
        # Pick top 15 predicted stocks based on the 'pred_score' column
        top_pred = day_data.nlargest(15, 'pred_score')
        
        scores = torch.tensor(top_pred['pred_score'].values)
        weights = torch.softmax(scores, dim=0).numpy()

        # Calculate the weighted average return instead of the simple mean
        actual_ret = np.sum(weights * top_pred["target_regression"]) - transaction_cost

     
        strategy_returns.append(actual_ret)
        
        # Calculate the market's return for this period
        market_returns.append(np.mean(day_data["target_regression"]))
    
    if not strategy_returns:
        print("Not enough data to run evaluation.")
        return {}
        
    n_periods = len(strategy_returns)
    trades_per_year = 252 // 5
    
    # --- Calculate Metrics ---
    equity_curve = np.cumprod([1 + r for r in strategy_returns])
    total_return = equity_curve[-1] - 1
    annual_strategy_return = (1 + total_return) ** (trades_per_year / n_periods) - 1
    
    market_curve = np.cumprod([1 + r for r in market_returns])
    total_market_return = market_curve[-1] - 1
    annual_market_return = (1 + total_market_return) ** (trades_per_year / n_periods) - 1
    
    alpha = annual_strategy_return - annual_market_return
    
    per_period_rf = risk_free_rate / trades_per_year
    excess_returns = [r - per_period_rf for r in strategy_returns]
    std_excess = np.std(excess_returns)
    sharpe = (np.mean(excess_returns) / std_excess * np.sqrt(trades_per_year)) if std_excess != 0 else 0.0
    
    hits = [1 if r > 0 else 0 for r in strategy_returns]
    win = [1 if r > m else 0 for r, m in zip(strategy_returns, market_returns)]
    hit_rate = np.mean(hits) * 100
    win_rate = np.mean(win) * 100

    # --- Print and Plot Results ---
    print("\n--- Financial Backtest Results ---")
    print(f"Annual Strategy Return: {annual_strategy_return:.2%}")
    print(f"Annual Market Return: {annual_market_return:.2%}")
    print(f"Excess Return (Alpha): {alpha:.2%}")
    print(f"Sharpe Ratio: {sharpe:.3f}")
    print(f"Hit Rate (Returns > 0): {hit_rate:.2f}%")
    print(f"Win Rate (Beat Market): {win_rate:.2f}%")
    
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve, label='Strategy Equity Curve')
    plt.plot(market_curve, label='Market Equity Curve')
    plt.title('Strategy vs. Market Performance')
    plt.xlabel('Trading Periods (every 5 days)')
    plt.ylabel('Cumulative Growth')
    plt.legend()
    plt.grid(True)
    plt.show()

    return {
        'annual_strategy_return': annual_strategy_return,
        'annual_market_return': annual_market_return,
        'alpha': alpha,
        'sharpe': sharpe
    }


if __name__ == '__main__':
  
    SCRIPT_DIR = Path(__file__).resolve().parent
    DATA_FILE_PATH = SCRIPT_DIR.parent / "data" / "processed" / "swing_trading_model_data.parquet"
    TENSOR_DIR = SCRIPT_DIR.parent / "data" / "tensors"
    MODEL_PATH = SCRIPT_DIR.parent / "models" / "lstm.pt"
    TARGET_COLUMN = 'target_sharpe'
    SEQUENCE_LENGTH = 30
    TRAIN_TEST_SPLIT_SIZE = 0.85

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    
    with open(TENSOR_DIR / 'feature_scaler.pkl', 'rb') as f:
        feature_scaler = pickle.load(f)
    with open(TENSOR_DIR / 'target_scaler.pkl', 'rb') as f:
        target_scaler = pickle.load(f)
        
    checkpoint = torch.load(MODEL_PATH, map_location=device)
    input_size = feature_scaler.n_features_in_
    model = BidirectionalLSTM(
        input_size=checkpoint['hparams']['input_size'],
        hidden_size=checkpoint['hparams']['hidden_size'],
        num_layers=checkpoint['hparams']['num_layers'],
        dropout_prob=checkpoint['hparams']['dropout_prob']
    ).to(device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    print("Model and scalers loaded successfully.")


    df = pd.read_parquet(DATA_FILE_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Date']).reset_index(drop=True)

    split_index = int(len(df) * TRAIN_TEST_SPLIT_SIZE)
    test_df = df.iloc[split_index:].copy() 
    test_df['daily_return'] =test_df.groupby('Ticker')['Close'].pct_change(1)
    test_df['future_vol_5d'] =test_df.groupby('Ticker')['daily_return'].transform(
        lambda x: x.rolling(5).std().shift(-5)
)       
    test_df['target_sharpe'] =(test_df['target_regression'] / test_df['future_vol_5d'] + 1e-6)
    test_df['rsi_rank'] =test_df.groupby('Date')['rsi_14d'].rank(pct=True)
    test_df['roc_rank'] =test_df.groupby('Date')['roc_21d'].rank(pct=True)
    test_df['avg_volume_30d'] =test_df.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(30).mean().shift(1))
    test_df['volume_buzz'] = (test_df['Volume'] /test_df['avg_volume_30d']).shift(1)
    test_df['spy_ma_200d'] =test_df['sp500_Close'].rolling(200).mean().shift(1)
    test_df['market_regime'] = (test_df['sp500_Close'] >test_df['spy_ma_200d']).astype(int).shift(1)
    test_df['month']=test_df['Date'].dt.month
    test_df['month_sin'] = np.sin(2 * np.pi *test_df['month'] / 12)
    test_df['month_cos'] = np.cos(2 * np.pi *test_df['month'] / 12)



    feature_cols = [
        'return_5d', 'rsi_14d', 'volatility_10d', 'volatility_20d',
        'sp500_return_5d', 'relative_strength_5d', "stochastic_k",
        "stochastic_d", 'ema_8_21_cross', 'ema_21d', 'ema_8d',
        'macd_histogram', 'obv_scaled', 'atr_14d', 'bollinger_percent_b',
        'roc_21d','rsi_rank', 'roc_rank','volume_buzz', 'market_regime',
        'month_sin','month_cos'
    ]

    test_df=test_df.dropna()


    features_test = test_df[feature_cols].to_numpy()
    

    features_test_scaled = feature_scaler.transform(features_test)
    
  
    X_test_seq = create_sequences(features_test_scaled, SEQUENCE_LENGTH)
    X_test_tensor = torch.tensor(X_test_seq, dtype=torch.float32).to(device)
    
    test_dataset=TensorDataset(X_test_tensor)
    test_loader=DataLoader(test_dataset, batch_size=256, shuffle=False)
  
  
    print("Making predictions on the test set...")
    model.eval()
    all_predictions=[]
    with torch.no_grad():
        for batch_X_tuple in test_loader:
            batch_X=batch_X_tuple[0].to(device)
            batch_pred=model(batch_X)
            all_predictions.append(batch_pred.cpu())
    predictions_scaled = torch.cat(all_predictions, dim=0).numpy()
    predictions_unscaled = target_scaler.inverse_transform(predictions_scaled)
    print("Aligning predictions with the DataFrame...")
    eval_df = test_df.iloc[SEQUENCE_LENGTH:].copy()

    if len(eval_df) == len(predictions_unscaled):
        eval_df['pred_score'] = predictions_unscaled
        evaluate_performance(eval_df)
    else:
        print(f"Error: Length mismatch. DataFrame has {len(eval_df)} rows, but model produced {len(predictions_unscaled)} predictions.")
