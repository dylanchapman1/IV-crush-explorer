import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { earningsApi } from './utils/api';
import EarningsTable from './components/EarningsTable';
import EarningsChart from './components/EarningsChart';
import ModelStatus from './components/ModelStatus';

function App() {
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);

  const { data: upcomingEarnings, isLoading, error } = useQuery({
    queryKey: ['upcomingEarnings'],
    queryFn: earningsApi.getUpcoming,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Earnings Predictor
          </h1>
          <p className="text-gray-600">
            AI-powered predictions for post-earnings stock moves with IV opportunity analysis
          </p>
        </header>

        <ModelStatus />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Upcoming Earnings Opportunities
              </h2>
              
              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              )}

              {error && (
                <div className="bg-red-50 border border-red-200 rounded-md p-4">
                  <p className="text-red-800">
                    Failed to load earnings data. Please try again later.
                  </p>
                </div>
              )}

              {upcomingEarnings && (
                <EarningsTable 
                  earnings={upcomingEarnings}
                  onSymbolSelect={setSelectedSymbol}
                />
              )}
            </div>
          </div>

          <div className="space-y-6">
            {selectedSymbol ? (
              <EarningsChart symbol={selectedSymbol} />
            ) : (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Select a Stock to View Chart
                  </h3>
                  <p className="text-gray-500">
                    Click on any stock symbol in the table to view its historical IV vs RV analysis
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;