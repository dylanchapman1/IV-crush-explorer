#!/usr/bin/env python3
"""
Data pipeline script to collect and process historical earnings data
Run this to build the initial dataset for training
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.data_collector import DataCollector

# Major stocks to include in our dataset
STOCK_SYMBOLS = [
    # Technology
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "NFLX", "CRM", "UBER",
    "ORCL", "ADBE", "INTC", "AMD", "PYPL", "SNOW", "PLTR", "ROKU", "ZM", "SQ",
    
    # Finance
    "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "AXP", "V", "MA",
    
    # Healthcare
    "JNJ", "PFE", "UNH", "MRNA", "ABBV", "TMO", "DHR", "BMY", "MRK", "LLY",
    
    # Consumer
    "WMT", "HD", "MCD", "NKE", "SBUX", "TGT", "COST", "LOW", "TJX", "DIS",
    
    # Energy & Materials
    "XOM", "CVX", "COP", "OXY", "SLB", "CAT", "DE", "MMM", "HON", "RTX"
]

def main():
    print("Starting data collection pipeline...")
    collector = DataCollector()
    
    print(f"Collecting data for {len(STOCK_SYMBOLS)} symbols...")
    historical_data = collector.build_historical_dataset(STOCK_SYMBOLS)
    
    print(f"\nDataset Summary:")
    print(f"Total records: {len(historical_data)}")
    print(f"Unique symbols: {historical_data['symbol'].nunique()}")
    print(f"Date range: {historical_data['earnings_date'].min()} to {historical_data['earnings_date'].max()}")
    print(f"Average absolute gap: {historical_data['overnight_gap_pct'].abs().mean():.2f}%")
    print(f"Average IV proxy: {historical_data['iv_proxy'].mean():.2f}%")
    
    print("\nData collection complete!")

if __name__ == "__main__":
    main()