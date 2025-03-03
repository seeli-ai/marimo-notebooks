import pandas as pd
import os
import ta
from ta.volatility import AverageTrueRange
from datetime import date


def calculate_atr(symbol, current_date:date, period=30, data_dir="data"):
    # Construct file path
    csv_path = os.path.join(data_dir, f"{symbol}.csv")
    
    # Check if file exists
    if not os.path.exists(csv_path):
        print(f"Error: Data file for {symbol} not found at {csv_path}")
        return None, None
    
    # Load the data
    df = pd.read_csv(csv_path)

    df['Date'] = pd.to_datetime(df['Date'], utc=True)

    df['Date'] = df['Date'].dt.date

    df.set_index('Date', inplace=True)
    
   
    # Calculate ATR
    atr_indicator = AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], window=period)
    df[f'ATR_{period}'] = atr_indicator.average_true_range()
    
    # Filter data to before the current date
    df_before = df[df.index < current_date]
    
    if df_before.empty:
        print(f"Error: No data available for {symbol} before {current_date}")
        return None, None
    
    # Get the last available ATR value and close price before the current date
    last_atr = df_before[f'ATR_{period}'].iloc[-1]
    last_close = df_before['Close'].iloc[-1]
    
    if pd.isna(last_atr):
        print(f"Warning: ATR value for {symbol} is NaN. May need more historical data for {period}-day ATR.")
        return None, last_close
    
    return last_atr, last_close