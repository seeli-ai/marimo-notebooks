import yfinance as yf
import os
import pandas as pd
from datetime import datetime, timedelta
import time

def download_stock_data(symbols, days=100, data_dir="data"):
    """
    Download daily stock data for the specified symbols and save to CSV files.
    
    Parameters:
    - symbols: List of stock symbols to download
    - days: Number of historical trading days to download
    - data_dir: Directory to save CSV files
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created directory: {data_dir}")
    
    # Calculate date range (add buffer days for weekends/holidays)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days * 1.5)  # Add 50% more days to account for weekends/holidays
    
    # Format dates for yfinance
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    successful_downloads = 0
    failed_downloads = []
    
    for symbol in symbols:
        try:
            print(f"Downloading data for {symbol}...")
            
            # Add .US suffix to ensure we get US exchange data
            ticker = yf.Ticker(f"{symbol}")
            
            # Get stock info to verify it's a US stock
            info = ticker.info
            
            # Check if it's a US exchange
            exchange = info.get('exchange', '')
            if exchange not in ['NYSE', 'NASDAQ', 'NYQ', 'NMS', 'NGM']:
                print(f"Warning: {symbol} may not be traded on a US exchange (found: {exchange}). Checking for US-specific data...")
                # We'll still try to download, but log the warning
            
            # Download historical data
            data = ticker.history(start=start_str, end=end_str, interval="1d")
            
            # Check if we got data
            if data.empty:
                print(f"No data found for {symbol}")
                failed_downloads.append((symbol, "No data returned"))
                continue
                
            # Limit to exactly the number of days requested (if available)
            if len(data) > days:
                data = data.iloc[-days:]
            
            # Save to CSV
            csv_path = os.path.join(data_dir, f"{symbol}.csv")
            data.to_csv(csv_path)
            
            print(f"Successfully downloaded {len(data)} days of data for {symbol}")
            successful_downloads += 1
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"Error downloading {symbol}: {str(e)}")
            failed_downloads.append((symbol, str(e)))
    
    # Print summary
    print(f"\nDownload Summary:")
    print(f"- Successfully downloaded data for {successful_downloads} symbols")
    print(f"- Failed to download data for {len(failed_downloads)} symbols")
    
    if failed_downloads:
        print("\nFailed downloads:")
        for symbol, error in failed_downloads:
            print(f"- {symbol}: {error}")




def load_stock_data(symbol, data_dir="data"):
    csv_path = os.path.join(data_dir, f"{symbol}.csv")
    if os.path.exists(csv_path):
        data = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        return data
    else:
        print(f"No data file found for {symbol}")
        return None