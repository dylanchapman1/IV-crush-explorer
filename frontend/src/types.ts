export interface UpcomingEarnings {
  symbol: string;
  earnings_date: string;
  current_price: number;
  iv_proxy: number;
  predicted_gap_pct?: number;
  opportunity_score?: number;
}

export interface HistoricalEarningsData {
  symbol: string;
  earnings_date: string;
  prev_close: number;
  post_open: number;
  overnight_gap_pct: number;
  five_day_realized_vol: number;
  iv_proxy: number;
  momentum_20d: number;
  beta_market: number;
  past_surprise?: number;
}

export interface EarningsHistoryResponse {
  symbol: string;
  historical_data: HistoricalEarningsData[];
}

export interface PredictionRequest {
  symbol: string;
  earnings_date: string;
  iv_proxy?: number;
  current_price?: number;
  momentum_20d?: number;
  beta_market?: number;
}

export interface PredictionResult {
  symbol: string;
  earnings_date: string;
  predicted_gap_pct: number;
  iv_proxy: number;
  opportunity_score: number;
}