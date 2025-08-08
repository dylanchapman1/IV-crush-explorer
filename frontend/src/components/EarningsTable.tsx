import React from 'react';
import { format, parseISO } from 'date-fns';
import { UpcomingEarnings } from '../types';

interface EarningsTableProps {
  earnings: UpcomingEarnings[];
  onSymbolSelect: (symbol: string) => void;
}

const EarningsTable: React.FC<EarningsTableProps> = ({ earnings, onSymbolSelect }) => {
  const formatPercent = (value?: number) => {
    if (value === undefined || value === null) return '-';
    return `${value.toFixed(1)}%`;
  };

  const formatCurrency = (value: number) => {
    return `$${value.toFixed(2)}`;
  };

  const getOpportunityBadge = (score?: number) => {
    if (score === undefined || score === null) return null;
    
    if (score > 5) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
          Overpriced
        </span>
      );
    } else if (score < -5) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Underpriced
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Neutral
        </span>
      );
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Symbol
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Earnings Date
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Current Price
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              IV Proxy
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Predicted Move
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Opportunity
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Score
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {earnings.map((earning) => (
            <tr 
              key={earning.symbol}
              className="hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => onSymbolSelect(earning.symbol)}
            >
              <td className="px-6 py-4 whitespace-nowrap">
                <div className="text-sm font-medium text-blue-600 hover:text-blue-800">
                  {earning.symbol}
                </div>
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {format(parseISO(earning.earnings_date), 'MMM dd, yyyy')}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatCurrency(earning.current_price)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatPercent(earning.iv_proxy)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatPercent(earning.predicted_gap_pct)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {getOpportunityBadge(earning.opportunity_score)}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {formatPercent(earning.opportunity_score)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      
      {earnings.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          No upcoming earnings data available
        </div>
      )}
    </div>
  );
};

export default EarningsTable;