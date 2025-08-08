# Earnings Predictor

A web application that predicts the magnitude of stock price moves after earnings announcements and identifies opportunities where implied volatility is mispriced relative to expected moves.

## Overview

This application uses machine learning to predict post-earnings stock price movements and compares these predictions to implied volatility proxies to identify potential trading opportunities. It features:

- **Historical Data Pipeline**: Collects stock prices, earnings dates, and calculates volatility metrics
- **ML Prediction Model**: LightGBM model trained on historical earnings data to predict move magnitude
- **IV vs RV Analysis**: Compares implied volatility proxies to realized volatility around earnings
- **Opportunity Ranking**: Identifies potentially overpriced or underpriced options before earnings

## Tech Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Web framework
- **pandas** - Data processing  
- **LightGBM** - Machine learning
- **yfinance** - Stock data
- **BeautifulSoup** - Web scraping

### Frontend
- **React 18** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Recharts** - Data visualization
- **Tanstack Query** - State management

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finproj
   ```

2. **Set up Python backend**
   ```bash
   cd backend
   pip install -r ../requirements.txt
   ```

3. **Set up React frontend**
   ```bash
   cd ../frontend
   npm install
   ```

### Data Pipeline Setup

4. **Collect historical data** (takes 5-10 minutes)
   ```bash
   cd backend
   python data_pipeline.py
   ```

5. **Train the ML model** (takes 2-5 minutes)
   ```bash
   python train_model.py
   ```

### Running the Application

6. **Start the backend API**
   ```bash
   cd backend
   python main.py
   ```
   Backend will run on http://localhost:8000

7. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on http://localhost:3000

## Usage

### Dashboard Features

1. **Upcoming Earnings Table**
   - Shows stocks with upcoming earnings dates
   - Displays IV proxy, predicted moves, and opportunity scores
   - Color-coded opportunity indicators (overpriced/underpriced/neutral)

2. **Historical Analysis Charts**
   - Click any symbol to view IV vs RV trends over time
   - Scatter plot showing prediction accuracy
   - Summary statistics for each stock

3. **Model Status**
   - Real-time model availability and performance metrics
   - Training date and feature count display

### Interpreting Results

- **Opportunity Score = IV Proxy - Predicted Move**
  - **Positive scores** (red): IV may be overpriced, potential sell opportunity
  - **Negative scores** (green): IV may be underpriced, potential buy opportunity
  - **Neutral scores** (yellow): Fair value, limited opportunity

- **IV Proxy**: Calculated from historical volatility and average true range
- **Predicted Move**: ML model prediction of absolute price change %

## API Endpoints

### Earnings
- `GET /api/earnings/upcoming` - Get upcoming earnings with predictions
- `GET /api/earnings/history/{symbol}` - Get historical data for symbol
- `GET /api/earnings/symbols` - Get available symbols

### Predictions  
- `POST /api/predictions/predict` - Make custom prediction
- `GET /api/predictions/model/status` - Get model status
- `POST /api/predictions/model/retrain` - Retrain model

## Data Sources

- **Stock Prices**: Yahoo Finance (via yfinance)
- **Earnings Dates**: Yahoo Finance calendar
- **Market Data**: S&P 500 (SPY) as market proxy

## Model Details

### Features Used
- IV proxy (historical volatility + ATR)
- 20-day price momentum
- Beta to market
- Sector classification
- Price level (log-transformed)
- Seasonal factors (day of week, month, quarter)

### Training Process
- Uses LightGBM regression
- Time series cross-validation
- Target: Absolute overnight gap percentage
- Performance: ~3-4% MAE on historical data

## Project Structure

```
finproj/
├── backend/
│   ├── app/
│   │   ├── models/          # Pydantic models
│   │   ├── routes/          # FastAPI routes
│   │   └── services/        # Business logic
│   ├── data/               # Cached data files
│   ├── models/             # Trained ML models
│   ├── data_pipeline.py    # Data collection script
│   ├── train_model.py      # Model training script
│   └── main.py             # FastAPI app entry point
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # API client
│   │   └── types.ts        # TypeScript types
│   ├── index.html
│   └── vite.config.ts
├── requirements.txt        # Python dependencies
├── package.json           # Node.js dependencies
└── README.md
```

## Development

### Adding New Features

1. **Backend**: Add routes in `backend/app/routes/`
2. **Frontend**: Add components in `frontend/src/components/`
3. **Data**: Modify `data_collector.py` for new data sources
4. **Models**: Update `model_trainer.py` for new features

### Testing

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests  
cd frontend
npm test
```

### Environment Variables

Create `.env` files for configuration:

**Backend (.env)**
```
API_HOST=0.0.0.0
API_PORT=8000
DATA_UPDATE_INTERVAL=3600
```

**Frontend (.env)**
```
VITE_API_BASE=http://localhost:8000
```

## Deployment

### Using Docker

1. **Build images**
   ```bash
   docker build -t earnings-predictor-backend ./backend
   docker build -t earnings-predictor-frontend ./frontend
   ```

2. **Run with docker-compose**
   ```bash
   docker-compose up
   ```

### Manual Deployment

**Backend (Railway/Render)**
1. Push to GitHub
2. Connect to Railway/Render
3. Set Python version to 3.9+
4. Install command: `pip install -r requirements.txt`
5. Start command: `cd backend && python main.py`

**Frontend (Vercel)**
1. Connect GitHub repository
2. Set build command: `cd frontend && npm run build`
3. Set output directory: `frontend/dist`
4. Set environment variable: `VITE_API_BASE=<backend-url>`

## Performance Considerations

- **Data Updates**: Run `data_pipeline.py` weekly to refresh earnings data
- **Model Retraining**: Retrain monthly or after significant market events
- **Caching**: Historical data is cached locally for faster loading
- **Rate Limits**: Yahoo Finance has rate limits, data collection is throttled

## Limitations

- Uses free data sources with potential delays
- IV proxy is estimated, not actual option implied volatility
- Model trained on historical data may not predict future performance
- Limited to US stocks with sufficient earnings history

## Future Enhancements

- Integration with real options data (Polygon.io, Tradier)
- Backtesting framework for strategy validation
- Real-time price updates via WebSocket
- SHAP feature importance visualization
- Email/SMS alerts for high-opportunity trades
- Portfolio tracking and P&L analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
1. Check the GitHub Issues page
2. Review the troubleshooting section below
3. Submit a new issue with relevant details

## Troubleshooting

### Common Issues

**"Model not found" error**
- Run `python train_model.py` to train the model

**"No training data" error** 
- Run `python data_pipeline.py` to collect data

**Frontend won't connect to API**
- Check that backend is running on port 8000
- Verify CORS settings in `main.py`
- Check environment variables

**Data collection fails**
- Verify internet connection
- Check if Yahoo Finance is accessible
- Try reducing the number of symbols in `data_pipeline.py`

**Slow performance**
- Reduce the number of symbols being processed
- Increase cache usage
- Consider using a faster machine for model training