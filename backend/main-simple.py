from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

app = FastAPI(title="Earnings Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Earnings Predictor API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/earnings/upcoming")
async def get_upcoming_earnings():
    # Mock data for now
    return [
        {
            "symbol": "AAPL",
            "earnings_date": "2024-01-25",
            "current_price": 195.89,
            "iv_proxy": 28.5,
            "predicted_gap_pct": 4.2,
            "opportunity_score": 24.3
        },
        {
            "symbol": "MSFT",
            "earnings_date": "2024-01-24",
            "current_price": 402.56,
            "iv_proxy": 22.1,
            "predicted_gap_pct": 3.8,
            "opportunity_score": 18.3
        },
        {
            "symbol": "GOOGL",
            "earnings_date": "2024-01-30",
            "current_price": 142.22,
            "iv_proxy": 31.2,
            "predicted_gap_pct": 5.5,
            "opportunity_score": 25.7
        }
    ]

@app.get("/api/earnings/history/{symbol}")
async def get_earnings_history(symbol: str):
    # Mock historical data
    return {
        "symbol": symbol,
        "historical_data": [
            {
                "symbol": symbol,
                "earnings_date": "2023-10-26",
                "prev_close": 170.29,
                "post_open": 175.84,
                "overnight_gap_pct": 3.26,
                "five_day_realized_vol": 25.3,
                "iv_proxy": 32.1,
                "momentum_20d": 8.4,
                "beta_market": 1.29
            },
            {
                "symbol": symbol,
                "earnings_date": "2023-07-27",
                "prev_close": 193.38,
                "post_open": 189.69,
                "overnight_gap_pct": -1.91,
                "five_day_realized_vol": 18.7,
                "iv_proxy": 28.9,
                "momentum_20d": 12.1,
                "beta_market": 1.29
            }
        ]
    }

@app.get("/api/predictions/model/status")
async def get_model_status():
    return {
        "available": True,
        "training_date": "2024-01-15T10:30:00",
        "performance": {"mae": 3.2, "rmse": 4.8, "r2": 0.65},
        "feature_count": 12
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)