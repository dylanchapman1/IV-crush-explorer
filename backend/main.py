from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import earnings, predictions
import uvicorn

app = FastAPI(title="Earnings Predictor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(earnings.router, prefix="/api/earnings", tags=["earnings"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])

@app.get("/")
async def root():
    return {"message": "Earnings Predictor API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)