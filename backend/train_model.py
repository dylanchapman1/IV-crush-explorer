#!/usr/bin/env python3
"""
Model training script
Run this after collecting data to train the earnings prediction model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.model_trainer import EarningsPredictor

def main():
    print("Starting model training...")
    
    predictor = EarningsPredictor()
    
    try:
        model = predictor.train_model()
        print("Model training completed successfully!")
        
        # Test prediction
        print("\nTesting model with sample prediction...")
        test_prediction = predictor.predict_single(
            symbol="AAPL",
            iv_proxy=25.0,
            momentum_20d=5.0,
            beta_market=1.2,
            prev_close=150.0
        )
        print(f"Sample prediction for AAPL: {test_prediction:.2f}% expected move")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run data_pipeline.py first to collect training data.")
    except Exception as e:
        print(f"Training failed: {e}")

if __name__ == "__main__":
    main()