from fastapi import APIRouter, HTTPException
from typing import List
import pandas as pd
from datetime import datetime, date
import os

from ..models.earnings import UpcomingEarnings, EarningsHistoryResponse, HistoricalEarningsData
from ..services.data_collector import DataCollector
from ..services.model_trainer import EarningsPredictor

router = APIRouter()

@router.get("/upcoming", response_model=List[UpcomingEarnings])
async def get_upcoming_earnings():
    """Get upcoming earnings with predictions and opportunity scores"""
    try:
        collector = DataCollector()
        predictor = EarningsPredictor()
        
        # Load model if available
        try:
            predictor.load_model()
            model_available = True
        except FileNotFoundError:
            model_available = False
        
        upcoming = collector.get_upcoming_earnings()
        results = []
        
        for item in upcoming:
            result = UpcomingEarnings(**item)
            
            # Add predictions if model is available
            if model_available:
                try:
                    predicted_gap = predictor.predict_single(
                        symbol=item['symbol'],
                        iv_proxy=item['iv_proxy'],
                        prev_close=item['current_price']
                    )
                    
                    result.predicted_gap_pct = predicted_gap
                    result.opportunity_score = item['iv_proxy'] - predicted_gap
                except Exception as e:
                    print(f"Prediction error for {item['symbol']}: {e}")
            
            results.append(result)
        
        # Sort by opportunity score (descending)
        if model_available:
            results.sort(key=lambda x: x.opportunity_score or 0, reverse=True)
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{symbol}", response_model=EarningsHistoryResponse)
async def get_earnings_history(symbol: str):
    """Get historical earnings data for a specific symbol"""
    try:
        data_path = "backend/data/historical_earnings.csv"
        
        if not os.path.exists(data_path):
            raise HTTPException(status_code=404, detail="Historical data not found. Run data pipeline first.")
        
        df = pd.read_csv(data_path)
        symbol_data = df[df['symbol'] == symbol.upper()]
        
        if len(symbol_data) == 0:
            raise HTTPException(status_code=404, detail=f"No historical data found for symbol {symbol}")
        
        historical_records = []
        for _, row in symbol_data.iterrows():
            record = HistoricalEarningsData(
                symbol=row['symbol'],
                earnings_date=datetime.strptime(row['earnings_date'], '%Y-%m-%d').date(),
                prev_close=row['prev_close'],
                post_open=row['post_open'],
                overnight_gap_pct=row['overnight_gap_pct'],
                five_day_realized_vol=row['five_day_realized_vol'],
                iv_proxy=row['iv_proxy'],
                momentum_20d=row['momentum_20d'],
                beta_market=row['beta_market'],
                past_surprise=row.get('past_surprise')
            )
            historical_records.append(record)
        
        # Sort by date (most recent first)
        historical_records.sort(key=lambda x: x.earnings_date, reverse=True)
        
        return EarningsHistoryResponse(
            symbol=symbol.upper(),
            historical_data=historical_records
        )
        
    except Exception as e:
        if "404" in str(e):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/symbols")
async def get_available_symbols():
    """Get list of symbols with historical data"""
    try:
        data_path = "backend/data/historical_earnings.csv"
        
        if not os.path.exists(data_path):
            return {"symbols": [], "count": 0}
        
        df = pd.read_csv(data_path)
        symbols = sorted(df['symbol'].unique().tolist())
        
        return {"symbols": symbols, "count": len(symbols)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))