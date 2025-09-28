import React from 'react';
import { 
  ChartBarIcon, 
  ClockIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import PieChart from '../Charts/PieChart';
import HorizontalBarChart from '../Charts/HorizontalBarChart';

const PerformanceWidget = ({ data = {} }) => {
  const {
    totalSignals = 0,
    successfulSignals = 0,
    successRate = 0,
    avgConfidence = 0,
    activeTracking = 0,
    uptime = 'N/A'
  } = data;

  const hasData = totalSignals > 0;

  // Prepare data for charts - ensure no NaN values
  const pieData = [
    { label: 'Successful', value: Math.max(0, successfulSignals || 0), color: '#10B981' },
    { label: 'Failed', value: Math.max(0, (totalSignals || 0) - (successfulSignals || 0)), color: '#EF4444' }
  ];

  const barData = [
    { label: 'Total', value: Math.max(0, totalSignals || 0), color: '#3B82F6' },
    { label: 'Success', value: Math.max(0, successfulSignals || 0), color: '#10B981' },
    { label: 'Confidence', value: Math.max(0, avgConfidence || 0), color: '#F59E0B' }
  ];

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          <ClockIcon className="w-4 h-4" />
          <span>{uptime}</span>
        </div>
      </div>

      {/* Performance Stats */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-blue-600">{totalSignals}</div>
          <div className="text-xs text-gray-500">Total Signals</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-green-600">{successfulSignals}</div>
          <div className="text-xs text-gray-500">Successful</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-purple-600">{successRate.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Success Rate</div>
        </div>
        <div className="text-center p-3 bg-gray-50 rounded-lg">
          <div className="text-xl font-bold text-orange-600">{avgConfidence.toFixed(1)}%</div>
          <div className="text-xs text-gray-500">Avg Confidence</div>
        </div>
      </div>

      {/* Charts Section - Moved to bottom */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        {/* Pie Chart */}
        <div className="text-center">
          <div className="mb-2">
            <PieChart data={pieData} size={100} />
          </div>
          
        </div>
        
        {/* Horizontal Bar Chart */}
        <div className="text-center">
          <div className="mb-2">
            <HorizontalBarChart data={barData} width={120} height={80} />
          </div>
          <div className="text-xs text-gray-600">Performance</div>
        </div>
      </div>

      {/* Active Tracking */}
      <div className="mb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <EyeIcon className="w-4 h-4 text-gray-500" />
            <span className="text-sm text-gray-600">Active Tracking</span>
          </div>
          <div className="text-sm font-medium text-gray-900">{activeTracking}</div>
        </div>
      </div>

      {/* Status */}
      <div className="text-center mb-6">
        {hasData ? (
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
            System Active
          </div>
        ) : (
          <div className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
            <div className="w-2 h-2 bg-gray-500 rounded-full mr-2"></div>
            No data
          </div>
        )}
      </div>

      {/* Informative Message */}
      <div className="text-center">
        <div className="text-xs text-gray-500 italic">
          {hasData ? (
            successRate >= 70 ? 
              "Excellent performance! Keep up the great work." :
              successRate >= 50 ?
                "Good performance. Room for improvement." :
                "Performance needs attention. Review strategies."
          ) : (
            "Waiting for trading data to analyze performance metrics."
          )}
        </div>
      </div>
    </div>
  );
};

export default PerformanceWidget;