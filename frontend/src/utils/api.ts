import axios from 'axios';
import { UpcomingEarnings, EarningsHistoryResponse, PredictionRequest, PredictionResult } from '../types';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const earningsApi = {
  getUpcoming: async (): Promise<UpcomingEarnings[]> => {
    const response = await api.get('/api/earnings/upcoming');
    return response.data;
  },

  getHistory: async (symbol: string): Promise<EarningsHistoryResponse> => {
    const response = await api.get(`/api/earnings/history/${symbol}`);
    return response.data;
  },

  getSymbols: async (): Promise<{ symbols: string[]; count: number }> => {
    const response = await api.get('/api/earnings/symbols');
    return response.data;
  },
};

export const predictionsApi = {
  predict: async (request: PredictionRequest): Promise<PredictionResult> => {
    const response = await api.post('/api/predictions/predict', request);
    return response.data;
  },

  getModelStatus: async (): Promise<any> => {
    const response = await api.get('/api/predictions/model/status');
    return response.data;
  },

  retrainModel: async (): Promise<any> => {
    const response = await api.post('/api/predictions/model/retrain');
    return response.data;
  },
};