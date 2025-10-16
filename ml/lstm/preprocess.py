# preprocess.py
import torch
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from pathlib import Path
import pickle
import gc

# Helper function to create sequences for a given DataFrame's data
def process_and_create_sequences(df, feature_cols, target_column, sequence_length):
    all_X, all_y = [], []
    
    # Group by ticker to create valid sequences for each stock
    for ticker, group in df.groupby('Ticker'):
        if len(group) > sequence_length:
            features = group[feature_cols].to_numpy()
            target = group[[target_column]].to_numpy()
            def create_sequences_for_ticker(features, target, seq_length):
                X, y = [], []
                for i in range(len(features) - seq_length):
                    X.append(features[i:i + seq_length])
                    y.append(target[i + seq_length])
                return np.array(X), np.array(y)

            X_seq, y_seq = create_sequences_for_ticker(features, target, sequence_length)
            all_X.append(X_seq)
            all_y.append(y_seq)
            
    return np.concatenate(all_X, axis=0), np.concatenate(all_y, axis=0)


if __name__ == '__main__':
 
    SCRIPT_DIR = Path(__file__).resolve().parent
    DATA_FILE_PATH = SCRIPT_DIR.parent / "data" / "processed" / "swing_trading_model_data.parquet"
    TENSOR_DIR = SCRIPT_DIR.parent / "data" / "tensors"
    TARGET_COLUMN = 'target_sharpe'
    SEQUENCE_LENGTH = 30
    TRAIN_TEST_SPLIT_SIZE = 0.90
    
    TENSOR_DIR.mkdir(parents=True, exist_ok=True)
    print("Starting data preparation...")


    df = pd.read_parquet(DATA_FILE_PATH)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values(['Date']).reset_index(drop=True)
    

    
    split_index = int(len(df) * TRAIN_TEST_SPLIT_SIZE)
    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()
    
    for data in [train_df, test_df]:
        data['daily_return'] = data.groupby('Ticker')['Close'].pct_change(1)
        data['future_vol_5d'] = data.groupby('Ticker')['daily_return'].transform(
        lambda x: x.rolling(5).std().shift(-5)
)       
        data['target_sharpe'] = data['target_regression'] / (data['future_vol_5d'] + 1e-6)
        data['rsi_rank'] = data.groupby('Date')['rsi_14d'].rank(pct=True)
        data['roc_rank'] = data.groupby('Date')['roc_21d'].rank(pct=True)
        data['avg_volume_30d'] = data.groupby('Ticker')['Volume'].transform(lambda x: x.rolling(30).mean().shift(1))
        data['volume_buzz'] = (data['Volume'] / data['avg_volume_30d']).shift(1)
        data['spy_ma_200d'] = data['sp500_Close'].rolling(200).mean().shift(1)
        data['market_regime'] = (data['sp500_Close'] > data['spy_ma_200d']).astype(int).shift(1)
        data['month']=data['Date'].dt.month
        data['month_sin'] = np.sin(2 * np.pi * data['month'] / 12)
        data['month_cos'] = np.cos(2 * np.pi * data['month'] / 12)

    feature_cols = [
        'return_5d', 'rsi_14d', 'volatility_10d', 'volatility_20d',
        'sp500_return_5d', 'relative_strength_5d', "stochastic_k",
        "stochastic_d", 'ema_8_21_cross', 'ema_21d', 'ema_8d',
        'macd_histogram', 'obv_scaled', 'atr_14d', 'bollinger_percent_b',
        'roc_21d','rsi_rank', 'roc_rank','volume_buzz', 'market_regime',
        'month_sin','month_cos'
    ]


    test_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    train_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    test_df=test_df.dropna()
    train_df=train_df.dropna()


    print("Processing and saving TRAINING data...")
    X_train, y_train = process_and_create_sequences(train_df, feature_cols, TARGET_COLUMN, SEQUENCE_LENGTH)
    

    num_samples_train, seq_len, num_features = X_train.shape
    X_train_reshaped = X_train.reshape(-1, num_features)
    
    feature_scaler = MinMaxScaler(feature_range=(-1, 1))
    X_train_scaled_reshaped = feature_scaler.fit_transform(X_train_reshaped)
    X_train_scaled = X_train_scaled_reshaped.reshape(num_samples_train, seq_len, num_features)
    
    target_scaler = MinMaxScaler(feature_range=(-1, 1))
    y_train_scaled = target_scaler.fit_transform(y_train)


    torch.save(torch.tensor(X_train_scaled, dtype=torch.float32), TENSOR_DIR / 'X_train.pt')
    torch.save(torch.tensor(y_train_scaled, dtype=torch.float32), TENSOR_DIR / 'y_train.pt')
    with open(TENSOR_DIR / 'feature_scaler.pkl', 'wb') as f:
        pickle.dump(feature_scaler, f)
    with open(TENSOR_DIR / 'target_scaler.pkl', 'wb') as f:
        pickle.dump(target_scaler, f)
    
    print("Training data saved.")


    print("Clearing training data from memory...")
    del X_train, y_train, X_train_scaled, y_train_scaled, train_df
    gc.collect()


    print("Processing and saving TEST data...")
    X_test, y_test = process_and_create_sequences(test_df, feature_cols, TARGET_COLUMN, SEQUENCE_LENGTH)
    

    with open(TENSOR_DIR / 'feature_scaler.pkl', 'rb') as f:
        feature_scaler = pickle.load(f)
    with open(TENSOR_DIR / 'target_scaler.pkl', 'rb') as f:
        target_scaler = pickle.load(f)
        

    num_samples_test, _, _ = X_test.shape
    X_test_reshaped = X_test.reshape(-1, num_features)
    X_test_scaled_reshaped = feature_scaler.transform(X_test_reshaped)
    X_test_scaled = X_test_scaled_reshaped.reshape(num_samples_test, seq_len, num_features)
    y_test_scaled = target_scaler.transform(y_test)
    
    # Save test tensors
    torch.save(torch.tensor(X_test_scaled, dtype=torch.float32), TENSOR_DIR / 'X_test.pt')
    torch.save(torch.tensor(y_test_scaled, dtype=torch.float32), TENSOR_DIR / 'y_test.pt')
    
    print("Test data saved.")
    print("\nPreprocessing complete.")