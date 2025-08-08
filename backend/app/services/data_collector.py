import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import json
import os

class DataCollector:
    def __init__(self):
        self.data_dir = "backend/data"
        os.makedirs(self.data_dir, exist_ok=True)
    
    def get_stock_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Get historical stock price data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_earnings_dates_yahoo(self, symbol: str) -> List[date]:
        """Scrape earnings dates from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            calendar = ticker.calendar
            if calendar is not None and not calendar.empty:
                return [pd.to_datetime(date).date() for date in calendar.index]
            else:
                return []
        except Exception as e:
            print(f"Error fetching earnings dates for {symbol}: {e}")
            return []
    
    def calculate_overnight_gap(self, data: pd.DataFrame, earnings_date: date) -> Dict:
        """Calculate overnight gap around earnings date"""
        earnings_dt = pd.Timestamp(earnings_date)
        
        # Find the trading day before earnings
        before_earnings = data[data.index < earnings_dt].tail(1)
        # Find the trading day of earnings
        on_earnings = data[data.index >= earnings_dt].head(1)
        
        if before_earnings.empty or on_earnings.empty:
            return {}
        
        prev_close = before_earnings['Close'].iloc[0]
        post_open = on_earnings['Open'].iloc[0]
        gap_pct = ((post_open - prev_close) / prev_close) * 100
        
        return {
            'prev_close': prev_close,
            'post_open': post_open,
            'overnight_gap_pct': gap_pct
        }
    
    def calculate_realized_volatility(self, data: pd.DataFrame, start_date: date, days: int = 5) -> float:
        """Calculate realized volatility over specified days after start_date"""
        start_dt = pd.Timestamp(start_date)
        end_dt = start_dt + timedelta(days=days)
        
        period_data = data[(data.index >= start_dt) & (data.index <= end_dt)]
        if len(period_data) < 2:
            return 0.0
        
        returns = period_data['Close'].pct_change().dropna()
        return returns.std() * np.sqrt(252) * 100  # Annualized volatility in %
    
    def calculate_iv_proxy(self, data: pd.DataFrame, reference_date: date) -> float:
        """Calculate IV proxy using historical volatility and ATR"""
        ref_dt = pd.Timestamp(reference_date)
        
        # Get 30 days of data before reference date
        lookback_data = data[data.index < ref_dt].tail(30)
        if len(lookback_data) < 20:
            return 0.0
        
        # Historical volatility (20-day)
        returns = lookback_data['Close'].pct_change().dropna()
        hv = returns.std() * np.sqrt(252) * 100
        
        # Average True Range (10-day)
        lookback_data = lookback_data.copy()
        lookback_data['High-Low'] = lookback_data['High'] - lookback_data['Low']
        lookback_data['High-Close'] = abs(lookback_data['High'] - lookback_data['Close'].shift(1))
        lookback_data['Low-Close'] = abs(lookback_data['Low'] - lookback_data['Close'].shift(1))
        lookback_data['TR'] = lookback_data[['High-Low', 'High-Close', 'Low-Close']].max(axis=1)
        atr = lookback_data['TR'].tail(10).mean()
        atr_pct = (atr / lookback_data['Close'].iloc[-1]) * 100
        
        # Combine HV and ATR for IV proxy
        iv_proxy = (hv * 0.7) + (atr_pct * 0.3 * np.sqrt(252))
        return iv_proxy
    
    def calculate_momentum_20d(self, data: pd.DataFrame, reference_date: date) -> float:
        """Calculate 20-day momentum before reference date"""
        ref_dt = pd.Timestamp(reference_date)
        
        before_ref = data[data.index < ref_dt]
        if len(before_ref) < 21:
            return 0.0
        
        current_price = before_ref['Close'].iloc[-1]
        price_20d_ago = before_ref['Close'].iloc[-21]
        
        momentum = ((current_price - price_20d_ago) / price_20d_ago) * 100
        return momentum
    
    def calculate_beta(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """Calculate beta relative to market (SPY)"""
        # Align dates
        aligned = pd.concat([stock_data['Close'], market_data['Close']], axis=1, keys=['stock', 'market']).dropna()
        
        if len(aligned) < 50:
            return 1.0
        
        stock_returns = aligned['stock'].pct_change().dropna()
        market_returns = aligned['market'].pct_change().dropna()
        
        if len(stock_returns) == 0 or len(market_returns) == 0:
            return 1.0
        
        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 1.0
        
        beta = covariance / market_variance
        return beta
    
    def get_market_data(self, period: str = "2y") -> pd.DataFrame:
        """Get SPY data as market proxy"""
        return self.get_stock_data("SPY", period)
    
    def build_historical_dataset(self, symbols: List[str]) -> pd.DataFrame:
        """Build complete historical dataset for given symbols"""
        all_data = []
        market_data = self.get_market_data()
        
        for symbol in symbols:
            print(f"Processing {symbol}...")
            stock_data = self.get_stock_data(symbol)
            if stock_data.empty:
                continue
            
            earnings_dates = self.get_earnings_dates_yahoo(symbol)
            if not earnings_dates:
                continue
            
            beta = self.calculate_beta(stock_data, market_data)
            
            for earnings_date in earnings_dates:
                # Skip if earnings date is too recent (need post-earnings data)
                if earnings_date > (datetime.now().date() - timedelta(days=7)):
                    continue
                
                gap_data = self.calculate_overnight_gap(stock_data, earnings_date)
                if not gap_data:
                    continue
                
                realized_vol = self.calculate_realized_volatility(stock_data, earnings_date)
                iv_proxy = self.calculate_iv_proxy(stock_data, earnings_date)
                momentum = self.calculate_momentum_20d(stock_data, earnings_date)
                
                row = {
                    'symbol': symbol,
                    'earnings_date': earnings_date,
                    'prev_close': gap_data['prev_close'],
                    'post_open': gap_data['post_open'],
                    'overnight_gap_pct': gap_data['overnight_gap_pct'],
                    'five_day_realized_vol': realized_vol,
                    'iv_proxy': iv_proxy,
                    'momentum_20d': momentum,
                    'beta_market': beta,
                    'past_surprise': None  # Would need earnings surprise data
                }
                all_data.append(row)
        
        df = pd.DataFrame(all_data)
        
        # Save to CSV
        csv_path = os.path.join(self.data_dir, "historical_earnings.csv")
        df.to_csv(csv_path, index=False)
        print(f"Saved {len(df)} records to {csv_path}")
        
        return df
    
    def get_upcoming_earnings(self) -> List[Dict]:
        """Get upcoming earnings dates for next 2 weeks"""
        # For MVP, we'll use a hardcoded list of major stocks with known earnings patterns
        major_stocks = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "CRM", "UBER"]
        upcoming = []
        
        for symbol in major_stocks:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                current_price = info.get('currentPrice', 0)
                
                # For demo purposes, create some mock upcoming earnings
                # In production, you'd scrape from earnings calendars
                mock_date = datetime.now().date() + timedelta(days=np.random.randint(1, 14))
                
                stock_data = self.get_stock_data(symbol, "6mo")
                if not stock_data.empty:
                    iv_proxy = self.calculate_iv_proxy(stock_data, datetime.now().date())
                    
                    upcoming.append({
                        'symbol': symbol,
                        'earnings_date': mock_date,
                        'current_price': current_price,
                        'iv_proxy': iv_proxy
                    })
            except Exception as e:
                print(f"Error processing {symbol}: {e}")
                continue
        
        return upcoming