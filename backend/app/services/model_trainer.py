import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from lightgbm import LGBMRegressor
import joblib
import os
from datetime import datetime

class EarningsPredictor:
    def __init__(self):
        self.model = None
        self.feature_columns = None
        self.model_path = "backend/models/earnings_predictor.joblib"
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for model training"""
        # Create target variable (absolute gap percentage)
        df['target'] = df['overnight_gap_pct'].abs()
        
        # Feature engineering
        features_df = df.copy()
        
        # Volatility features
        features_df['iv_proxy_log'] = np.log1p(features_df['iv_proxy'])
        features_df['realized_vol_log'] = np.log1p(features_df['five_day_realized_vol'])
        features_df['vol_ratio'] = features_df['iv_proxy'] / (features_df['five_day_realized_vol'] + 1e-6)
        
        # Price momentum features
        features_df['momentum_20d_abs'] = features_df['momentum_20d'].abs()
        features_df['momentum_20d_sign'] = np.sign(features_df['momentum_20d'])
        
        # Beta features
        features_df['beta_deviation'] = features_df['beta_market'] - 1.0
        features_df['beta_squared'] = features_df['beta_market'] ** 2
        
        # Price level features
        features_df['price_log'] = np.log1p(features_df['prev_close'])
        
        # Seasonal features (day of week, month)
        features_df['earnings_date'] = pd.to_datetime(features_df['earnings_date'])
        features_df['day_of_week'] = features_df['earnings_date'].dt.dayofweek
        features_df['month'] = features_df['earnings_date'].dt.month
        features_df['quarter'] = features_df['earnings_date'].dt.quarter
        
        # Sector encoding (simplified)
        tech_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'NFLX', 'CRM', 'UBER', 'ORCL', 'ADBE', 'INTC', 'AMD', 'PYPL', 'SNOW', 'PLTR', 'ROKU', 'ZM', 'SQ']
        finance_symbols = ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'BLK', 'AXP', 'V', 'MA']
        healthcare_symbols = ['JNJ', 'PFE', 'UNH', 'MRNA', 'ABBV', 'TMO', 'DHR', 'BMY', 'MRK', 'LLY']
        
        features_df['sector_tech'] = features_df['symbol'].isin(tech_symbols).astype(int)
        features_df['sector_finance'] = features_df['symbol'].isin(finance_symbols).astype(int)
        features_df['sector_healthcare'] = features_df['symbol'].isin(healthcare_symbols).astype(int)
        
        return features_df
    
    def train_model(self, data_path: str = "backend/data/historical_earnings.csv"):
        """Train the earnings prediction model"""
        print("Loading training data...")
        df = pd.read_csv(data_path)
        print(f"Loaded {len(df)} records")
        
        if len(df) == 0:
            raise ValueError("No training data available. Run data_pipeline.py first.")
        
        # Prepare features
        features_df = self.prepare_features(df)
        
        # Remove rows with missing values
        features_df = features_df.dropna()
        print(f"Training on {len(features_df)} records after removing NaN values")
        
        # Define feature columns
        self.feature_columns = [
            'iv_proxy', 'iv_proxy_log', 'realized_vol_log', 'vol_ratio',
            'momentum_20d', 'momentum_20d_abs', 'momentum_20d_sign',
            'beta_market', 'beta_deviation', 'beta_squared',
            'price_log', 'day_of_week', 'month', 'quarter',
            'sector_tech', 'sector_finance', 'sector_healthcare'
        ]
        
        X = features_df[self.feature_columns]
        y = features_df['target']
        
        # Time series split for validation
        tscv = TimeSeriesSplit(n_splits=3)
        
        # Train model
        self.model = LGBMRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=6,
            num_leaves=31,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        
        # Cross-validation
        print("Performing cross-validation...")
        cv_scores = cross_val_score(self.model, X, y, cv=tscv, scoring='neg_mean_absolute_error')
        print(f"CV MAE: {-cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
        
        # Train final model
        print("Training final model...")
        self.model.fit(X, y)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\nTop 10 Feature Importances:")
        print(feature_importance.head(10))
        
        # Final evaluation
        y_pred = self.model.predict(X)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        r2 = r2_score(y, y_pred)
        
        print(f"\nFinal Model Performance:")
        print(f"MAE: {mae:.3f}%")
        print(f"RMSE: {rmse:.3f}%")
        print(f"R²: {r2:.3f}")
        
        # Save model
        print(f"Saving model to {self.model_path}")
        joblib.dump({
            'model': self.model,
            'feature_columns': self.feature_columns,
            'training_date': datetime.now().isoformat(),
            'performance': {'mae': mae, 'rmse': rmse, 'r2': r2}
        }, self.model_path)
        
        return self.model
    
    def load_model(self):
        """Load trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}. Train model first.")
        
        model_data = joblib.load(self.model_path)
        self.model = model_data['model']
        self.feature_columns = model_data['feature_columns']
        
        print(f"Model loaded from {self.model_path}")
        return self.model
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data"""
        if self.model is None:
            self.load_model()
        
        # Prepare features
        features_prepared = self.prepare_features(features)
        X = features_prepared[self.feature_columns]
        
        predictions = self.model.predict(X)
        return predictions
    
    def predict_single(self, symbol: str, iv_proxy: float, momentum_20d: float = 0, 
                      beta_market: float = 1.0, prev_close: float = 100) -> float:
        """Make prediction for a single stock"""
        # Create dummy data for prediction
        dummy_data = pd.DataFrame({
            'symbol': [symbol],
            'earnings_date': [datetime.now().date()],
            'prev_close': [prev_close],
            'post_open': [prev_close],  # Dummy value
            'overnight_gap_pct': [0],  # Dummy value
            'five_day_realized_vol': [iv_proxy * 0.8],  # Estimate
            'iv_proxy': [iv_proxy],
            'momentum_20d': [momentum_20d],
            'beta_market': [beta_market],
            'past_surprise': [None]
        })
        
        prediction = self.predict(dummy_data)[0]
        return prediction