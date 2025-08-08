import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts';
import { format, parseISO } from 'date-fns';
import { earningsApi } from '../utils/api';

interface EarningsChartProps {
  symbol: string;
}

const EarningsChart: React.FC<EarningsChartProps> = ({ symbol }) => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['earningsHistory', symbol],
    queryFn: () => earningsApi.getHistory(symbol),
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {symbol} - IV vs RV Analysis
        </h3>
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {symbol} - IV vs RV Analysis
        </h3>
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">
            Failed to load historical data for {symbol}
          </p>
        </div>
      </div>
    );
  }

  if (!data || data.historical_data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {symbol} - IV vs RV Analysis
        </h3>
        <div className="text-center py-12">
          <p className="text-gray-500">
            No historical data available for {symbol}
          </p>
        </div>
      </div>
    );
  }

  // Prepare data for charts
  const timeSeriesData = data.historical_data
    .slice()
    .reverse()
    .map((item, index) => ({
      date: format(parseISO(item.earnings_date), 'MMM yyyy'),
      ivProxy: item.iv_proxy,
      realizedVol: item.five_day_realized_vol,
      actualMove: Math.abs(item.overnight_gap_pct),
      index,
    }));

  const scatterData = data.historical_data.map((item) => ({
    ivProxy: item.iv_proxy,
    realizedVol: item.five_day_realized_vol,
    actualMove: Math.abs(item.overnight_gap_pct),
    date: item.earnings_date,
  }));

  const formatTooltip = (value: number, name: string) => {
    return [`${value.toFixed(1)}%`, name];
  };

  const formatLabel = (label: string) => {
    return `Date: ${label}`;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          {symbol} - Historical IV vs RV Trends
        </h3>
        
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="date"
                angle={-45}
                textAnchor="end"
                height={80}
                fontSize={12}
              />
              <YAxis 
                label={{ value: 'Volatility (%)', angle: -90, position: 'insideLeft' }}
                fontSize={12}
              />
              <Tooltip 
                formatter={formatTooltip}
                labelFormatter={formatLabel}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="ivProxy" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="IV Proxy"
                dot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="realizedVol" 
                stroke="#10B981" 
                strokeWidth={2}
                name="5-Day Realized Vol"
                dot={{ r: 4 }}
              />
              <Line 
                type="monotone" 
                dataKey="actualMove" 
                stroke="#F59E0B" 
                strokeWidth={2}
                name="Actual Move"
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          IV Proxy vs Actual Move Scatter Plot
        </h3>
        
        <div className="h-80 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid />
              <XAxis 
                type="number" 
                dataKey="ivProxy" 
                name="IV Proxy"
                label={{ value: 'IV Proxy (%)', position: 'insideBottom', offset: -10 }}
              />
              <YAxis 
                type="number" 
                dataKey="actualMove" 
                name="Actual Move"
                label={{ value: 'Actual Move (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                cursor={{ strokeDasharray: '3 3' }}
                formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, name]}
              />
              <Scatter 
                name="Earnings Events" 
                data={scatterData} 
                fill="#8884d8"
              />
              {/* Perfect prediction line */}
              <Line 
                data={[{ivProxy: 0, actualMove: 0}, {ivProxy: 50, actualMove: 50}]}
                stroke="#EF4444"
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Perfect Prediction"
                dot={false}
              />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm font-medium text-blue-800">Average IV Proxy</div>
            <div className="text-xl font-bold text-blue-900">
              {(data.historical_data.reduce((sum, item) => sum + item.iv_proxy, 0) / data.historical_data.length).toFixed(1)}%
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-sm font-medium text-green-800">Average Realized Vol</div>
            <div className="text-xl font-bold text-green-900">
              {(data.historical_data.reduce((sum, item) => sum + item.five_day_realized_vol, 0) / data.historical_data.length).toFixed(1)}%
            </div>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="text-sm font-medium text-yellow-800">Average Actual Move</div>
            <div className="text-xl font-bold text-yellow-900">
              {(data.historical_data.reduce((sum, item) => sum + Math.abs(item.overnight_gap_pct), 0) / data.historical_data.length).toFixed(1)}%
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EarningsChart;