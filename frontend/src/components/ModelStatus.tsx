import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { predictionsApi } from '../utils/api';

const ModelStatus: React.FC = () => {
  const { data: modelStatus, isLoading, error } = useQuery({
    queryKey: ['modelStatus'],
    queryFn: predictionsApi.getModelStatus,
  });

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
        <div className="animate-pulse flex items-center">
          <div className="rounded-full bg-gray-200 h-3 w-3 mr-3"></div>
          <div className="h-4 bg-gray-200 rounded w-24"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <div className="flex items-center">
          <div className="rounded-full bg-red-400 h-3 w-3 mr-3"></div>
          <div className="text-red-800 text-sm font-medium">
            Model Status: Error
          </div>
        </div>
      </div>
    );
  }

  if (!modelStatus?.available) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="rounded-full bg-yellow-400 h-3 w-3 mr-3"></div>
            <div className="text-yellow-800 text-sm font-medium">
              Model Status: Not Available
            </div>
          </div>
          <div className="text-yellow-700 text-xs">
            Run data pipeline and train model to enable predictions
          </div>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  const formatMetric = (value?: number) => {
    return value ? value.toFixed(3) : 'N/A';
  };

  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className="rounded-full bg-green-400 h-3 w-3 mr-3"></div>
          <div className="text-green-800 text-sm font-medium">
            Model Status: Active
          </div>
        </div>
        <div className="flex items-center space-x-4 text-green-700 text-xs">
          <span>Trained: {formatDate(modelStatus.training_date)}</span>
          <span>Features: {modelStatus.feature_count}</span>
          {modelStatus.performance && (
            <>
              <span>MAE: {formatMetric(modelStatus.performance.mae)}%</span>
              <span>R²: {formatMetric(modelStatus.performance.r2)}</span>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ModelStatus;