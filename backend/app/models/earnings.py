from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class HistoricalEarningsData(BaseModel):
    symbol: str
    earnings_date: date
    prev_close: float
    post_open: float
    overnight_gap_pct: float
    five_day_realized_vol: float
    iv_proxy: float
    momentum_20d: float
    beta_market: float
    past_surprise: Optional[float] = None

class PredictionResult(BaseModel):
    symbol: str
    earnings_date: date
    predicted_gap_pct: float
    iv_proxy: float
    opportunity_score: float

class UpcomingEarnings(BaseModel):
    symbol: str
    earnings_date: date
    current_price: float
    iv_proxy: float
    predicted_gap_pct: Optional[float] = None
    opportunity_score: Optional[float] = None

class EarningsHistoryResponse(BaseModel):
    symbol: str
    historical_data: list[HistoricalEarningsData]