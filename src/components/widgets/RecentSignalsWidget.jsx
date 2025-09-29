import React from 'react';
import { 
  ChartBarIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

const RecentSignalsWidget = ({ data = [] }) => {
  const signals = data || [];
  const hasData = signals.length > 0;

  const getSignalIcon = (direction) => {
    return direction === 'BUY' ? (
      <ArrowUpIcon className="w-4 h-4 text-green-500" />
    ) : (
      <ArrowDownIcon className="w-4 h-4 text-red-500" />
    );
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600 bg-green-50';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-50';
    if (confidence >= 40) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'text-blue-600 bg-blue-50';
      case 'TP1_HIT': return 'text-green-600 bg-green-50';
      case 'TP2_HIT': return 'text-green-600 bg-green-50';
      case 'TP3_HIT': return 'text-green-600 bg-green-50';
      case 'SL_HIT': return 'text-red-600 bg-red-50';
      case 'CLOSED': return 'text-gray-600 bg-gray-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const formatStatus = (status) => {
    switch (status) {
      case 'ACTIVE': return 'Active';
      case 'TP1_HIT': return 'TP1 Hit';
      case 'TP2_HIT': return 'TP2 Hit';
      case 'TP3_HIT': return 'TP3 Hit';
      case 'SL_HIT': return 'Stop Loss';
      case 'CLOSED': return 'Closed';
      default: return status;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <ChartBarIcon className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Recent Signals</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          <ClockIcon className="w-4 h-4" />
          <span>{signals.length}</span>
        </div>
      </div>

      {/* Signals List */}
      <div className="space-y-2">
        {hasData ? (
          signals.slice(0, 8).map((signal, index) => (
            <div key={signal.signal_id || index} className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-3 border border-gray-200 hover:shadow-md transition-all duration-200">
              {/* Header */}
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-3">
                  {getSignalIcon(signal.direction)}
                  <div>
                    <div className="font-semibold text-gray-900">{signal.symbol}</div>
                    <div className="text-sm text-gray-600">{signal.direction}</div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(signal.confidence)}`}>
                    {signal.confidence?.toFixed(1)}%
                  </span>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(signal.status)}`}>
                    {formatStatus(signal.status)}
                  </span>
                </div>
              </div>
              
              {/* Price Information - Compact */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex justify-between">
                  <span className="text-gray-600">Entry:</span>
                  <span className="font-medium text-gray-900">${signal.entry_price?.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Current:</span>
                  <span className="font-medium text-gray-900">${signal.current_price?.toFixed(4)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">TP1:</span>
                  <span className={`font-medium ${signal.tp1_hit ? 'text-green-700 bg-green-100 px-1 py-0.5 rounded' : 'text-green-600'}`}>
                    ${signal.tp1?.toFixed(4)} {signal.tp1_hit ? '✓' : ''}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">TP2:</span>
                  <span className={`font-medium ${signal.tp2_hit ? 'text-green-700 bg-green-100 px-1 py-0.5 rounded' : 'text-green-600'}`}>
                    ${signal.tp2?.toFixed(4)} {signal.tp2_hit ? '✓' : ''}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">TP3:</span>
                  <span className={`font-medium ${signal.tp3_hit ? 'text-green-700 bg-green-100 px-1 py-0.5 rounded' : 'text-green-600'}`}>
                    ${signal.tp3?.toFixed(4)} {signal.tp3_hit ? '✓' : ''}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">SL:</span>
                  <span className={`font-medium ${signal.stop_loss_hit ? 'text-red-700 bg-red-100 px-1 py-0.5 rounded' : 'text-red-600'}`}>
                    ${signal.stop_loss?.toFixed(4)} {signal.stop_loss_hit ? '✓' : ''}
                  </span>
                </div>
              </div>
              
              {/* Footer - Compact */}
              <div className="mt-2 pt-2 border-t border-gray-300">
                <div className="flex justify-between items-center text-xs text-gray-500">
                  <span>{new Date(signal.timestamp).toLocaleString()}</span>
                  <span>R/R: {signal.risk_reward_ratio?.toFixed(2)}</span>
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <ChartBarIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">No recent signals</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentSignalsWidget;