from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date

from ..models.earnings import PredictionResult
from ..services.model_trainer import EarningsPredictor
from ..services.data_collector import DataCollector

router = APIRouter()

class PredictionRequest(BaseModel):
    symbol: str
    earnings_date: date
    iv_proxy: Optional[float] = None
    current_price: Optional[float] = None
    momentum_20d: Optional[float] = 0.0
    beta_market: Optional[float] = 1.0

@router.post("/predict", response_model=PredictionResult)
async def predict_earnings_move(request: PredictionRequest):
    """Predict earnings move for a specific stock"""
    try:
        predictor = EarningsPredictor()
        collector = DataCollector()
        
        # Load model
        try:
            predictor.load_model()
        except FileNotFoundError:
            raise HTTPException(status_code=503, detail="Prediction model not available. Train model first.")
        
        # Get current data if not provided
        if request.iv_proxy is None or request.current_price is None:
            stock_data = collector.get_stock_data(request.symbol, "6mo")
            if stock_data.empty:
                raise HTTPException(status_code=404, detail=f"Could not fetch data for symbol {request.symbol}")
            
            if request.iv_proxy is None:
                request.iv_proxy = collector.calculate_iv_proxy(stock_data, request.earnings_date)
            
            if request.current_price is None:
                request.current_price = stock_data['Close'].iloc[-1]
        
        # Make prediction
        predicted_gap = predictor.predict_single(
            symbol=request.symbol,
            iv_proxy=request.iv_proxy,
            momentum_20d=request.momentum_20d,
            beta_market=request.beta_market,
            prev_close=request.current_price
        )
        
        # Calculate opportunity score
        opportunity_score = request.iv_proxy - predicted_gap
        
        return PredictionResult(
            symbol=request.symbol,
            earnings_date=request.earnings_date,
            predicted_gap_pct=predicted_gap,
            iv_proxy=request.iv_proxy,
            opportunity_score=opportunity_score
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/status")
async def get_model_status():
    """Get model training status and performance metrics"""
    try:
        import joblib
        import os
        
        model_path = "backend/models/earnings_predictor.joblib"
        
        if not os.path.exists(model_path):
            return {
                "available": False,
                "message": "Model not trained yet"
            }
        
        model_data = joblib.load(model_path)
        
        return {
            "available": True,
            "training_date": model_data.get('training_date'),
            "performance": model_data.get('performance', {}),
            "feature_count": len(model_data.get('feature_columns', []))
        }
        
    except Exception as e:
        return {
            "available": False,
            "error": str(e)
        }

@router.post("/model/retrain")
async def retrain_model():
    """Retrain the prediction model with latest data"""
    try:
        from ..services.model_trainer import EarningsPredictor
        
        predictor = EarningsPredictor()
        model = predictor.train_model()
        
        return {
            "success": True,
            "message": "Model retrained successfully"
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Training data not found. Run data pipeline first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")