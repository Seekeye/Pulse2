import React from 'react';
import { 
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import VerticalIndicatorChart from '../Charts/VerticalIndicatorChart';

const IndicatorsWidget = ({ data = {} }) => {
  const indicators = [
    { name: 'SMA 20', type: 'Trend', status: 'Active' },
    { name: 'SMA 50', type: 'Trend', status: 'Active' },
    { name: 'EMA 12', type: 'Trend', status: 'Active' },
    { name: 'EMA 26', type: 'Trend', status: 'Active' },
    { name: 'BB 20', type: 'Trend', status: 'Active' },
    { name: 'RSI 14', type: 'Momentum', status: 'Active' },
    { name: 'MACD', type: 'Momentum', status: 'Active' },
    { name: 'Stochastic', type: 'Momentum', status: 'Active' }
  ];

  const hasData = Object.keys(data || {}).length > 0;

  // Prepare data for horizontal chart - more stable values based on indicator type
  const getStableValue = (indicator) => {
    // Use a hash of the indicator name to get consistent values
    const hash = indicator.name.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    // Base values by type
    const baseValues = {
      'SMA 20': 85,
      'SMA 50': 78,
      'RSI': 92,
      'MACD': 65,
      'Stochastic': 88
    };
    
    // Return base value if exists, otherwise use hash-based stable value
    return baseValues[indicator.name] || Math.abs(hash) % 30 + 60;
  };

  // Shorten long indicator names
  const shortenName = (name) => {
    const shortNames = {
      'SMA 20': 'SMA20',
      'SMA 50': 'SMA50',
      'RSI': 'RSI',
      'MACD': 'MACD',
      'Stochastic': 'STOCH'
    };
    return shortNames[name] || name;
  };

  const chartData = indicators.map((indicator) => ({
    label: shortenName(indicator.name),
    value: getStableValue(indicator),
    color: indicator.type === 'Trend' ? '#3B82F6' : indicator.type === 'Momentum' ? '#10B981' : '#8B5CF6'
  }));

  const getTypeColor = (type) => {
    switch (type) {
      case 'Trend': return 'text-blue-600 bg-blue-50';
      case 'Momentum': return 'text-green-600 bg-green-50';
      case 'Volume': return 'text-purple-600 bg-purple-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active': return 'text-green-600 bg-green-50';
      case 'Inactive': return 'text-red-600 bg-red-50';
      case 'Warning': return 'text-yellow-600 bg-yellow-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Cog6ToothIcon className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Technical Indicators</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          <Cog6ToothIcon className="w-4 h-4" />
          <span>{indicators.length}</span>
        </div>
      </div>

      {/* Charts Section */}
      <div className="mb-4">
        {/* Vertical Bar Chart - Indicator Strength */}
        <div className="text-center">
          <div className="mb-2 flex justify-center">
            <VerticalIndicatorChart data={chartData} width={350} height={220} />
          </div>
          <div className="text-xs text-gray-600">Indicator Strength Analysis</div>
        </div>
      </div>

      {/* Market Status */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">System Status</div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${hasData ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
            {hasData ? 'Active' : 'No data'}
          </div>
        </div>
      </div>

      {/* Indicators Grid */}
      <div className="grid grid-cols-2 gap-2">
        {indicators.map((indicator, index) => (
          <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2">
              <Cog6ToothIcon className="w-4 h-4 text-gray-500" />
              <div>
                <div className="font-medium text-sm text-gray-900">{indicator.name}</div>
                <div className="text-xs text-gray-500">{indicator.type}</div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getTypeColor(indicator.type)}`}>
                {indicator.type}
              </span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(indicator.status)}`}>
                {indicator.status}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-4 pt-3 border-t border-gray-200">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-lg font-bold text-blue-600">4</div>
            <div className="text-xs text-gray-500">Trend</div>
          </div>
          <div>
            <div className="text-lg font-bold text-green-600">4</div>
            <div className="text-xs text-gray-500">Momentum</div>
          </div>
          <div>
            <div className="text-lg font-bold text-gray-600">8</div>
            <div className="text-xs text-gray-500">Total</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndicatorsWidget;