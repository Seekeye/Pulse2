import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ArrowUpIcon, 
  ArrowDownIcon,
  EyeIcon,
  ClockIcon,
  InformationCircleIcon,
  BoltIcon
} from '@heroicons/react/24/outline';


const ActiveSignalsWidget = ({ data = [] }) => {
  const [hoveredSignal, setHoveredSignal] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const totalSignals = data.length;

  // Update timestamp when data changes
  useEffect(() => {
    setLastUpdate(new Date());
  }, [data]);
  const buySignals = data.filter(signal => signal.direction === 'BUY').length;
  const sellSignals = data.filter(signal => signal.direction === 'SELL').length;

  const getSignalIcon = (direction) => {
    return direction === 'BUY' ? (
      <ArrowUpIcon className="w-4 h-4 text-green-500" />
    ) : (
      <ArrowDownIcon className="w-4 h-4 text-red-500" />
    );
  };

  const getSignalStatus = (signal) => {
    // Check if signal has been reinforced or is in conflict
    if (signal.reinforced_count && signal.reinforced_count > 0) {
      return {
        type: 'reinforced',
        text: `+${signal.reinforced_count} refuerzos`,
        color: 'bg-blue-100 text-blue-800',
        icon: '💪'
      };
    }
    if (signal.conflict_count && signal.conflict_count > 0) {
      return {
        type: 'conflict',
        text: `${signal.conflict_count} conflictos`,
        color: 'bg-orange-100 text-orange-800',
        icon: '⚠️'
      };
    }
    return null;
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-green-600 bg-green-50';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-50';
    if (confidence >= 40) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const formatTooltipContent = (signal) => {
    const profitTp1 = signal.tp1 ? ((signal.tp1 - signal.entry_price) / signal.entry_price * 100).toFixed(1) : 'N/A';
    const profitTp2 = signal.tp2 ? ((signal.tp2 - signal.entry_price) / signal.entry_price * 100).toFixed(1) : 'N/A';
    const profitTp3 = signal.tp3 ? ((signal.tp3 - signal.entry_price) / signal.entry_price * 100).toFixed(1) : 'N/A';
    const lossSl = signal.stop_loss ? ((signal.stop_loss - signal.entry_price) / signal.entry_price * 100).toFixed(1) : 'N/A';

    return (
      <div className="space-y-2">
        <div className="font-semibold text-gray-900 border-b border-gray-200 pb-2">
          {signal.symbol} - {signal.direction}
        </div>
        
        <div className="space-y-1 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Precio Actual:</span>
            <span className="font-medium">${signal.current_price?.toFixed(4) || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Precio Entrada:</span>
            <span className="font-medium">${signal.entry_price?.toFixed(4) || 'N/A'}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Confianza:</span>
            <span className="font-medium">{signal.confidence?.toFixed(1) || 'N/A'}%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Risk/Reward:</span>
            <span className="font-medium">{signal.risk_reward_ratio?.toFixed(2) || 'N/A'}</span>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-2">
          <div className="text-xs font-semibold text-gray-700 mb-1">Take Profits:</div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-600">TP1:</span>
              <span className="font-medium text-green-600">${signal.tp1?.toFixed(4) || 'N/A'} (+{profitTp1}%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">TP2:</span>
              <span className="font-medium text-green-600">${signal.tp2?.toFixed(4) || 'N/A'} (+{profitTp2}%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">TP3:</span>
              <span className="font-medium text-green-600">${signal.tp3?.toFixed(4) || 'N/A'} (+{profitTp3}%)</span>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 pt-2">
          <div className="text-xs font-semibold text-gray-700 mb-1">Stop Loss:</div>
          <div className="flex justify-between text-xs">
            <span className="text-gray-600">SL:</span>
            <span className="font-medium text-red-600">${signal.stop_loss?.toFixed(4) || 'N/A'} ({lossSl}%)</span>
          </div>
        </div>

        {/* Signal Status - Reinforcements/Conflicts */}
        {(signal.reinforced_count > 0 || signal.conflict_count > 0) && (
          <div className="border-t border-gray-200 pt-2">
            <div className="text-xs font-semibold text-gray-700 mb-1">Estado de la Señal:</div>
            <div className="space-y-1 text-xs">
              {signal.reinforced_count > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Refuerzos:</span>
                  <span className="font-medium text-blue-600">+{signal.reinforced_count}</span>
                </div>
              )}
              {signal.conflict_count > 0 && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Conflictos:</span>
                  <span className="font-medium text-orange-600">{signal.conflict_count}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {signal.reasoning && (
          <div className="border-t border-gray-200 pt-2">
            <div className="text-xs font-semibold text-gray-700 mb-1">Análisis:</div>
            <div className="text-xs text-gray-600 italic">{signal.reasoning}</div>
          </div>
        )}

        <div className="border-t border-gray-200 pt-2">
          <div className="text-xs text-gray-500">
            Creado: {new Date(signal.timestamp).toLocaleString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="mb-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <BoltIcon className="w-5 h-5 text-blue-600" />
                        <h3 className="text-lg font-semibold text-gray-900">Active Signals</h3>
                      </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Live</span>
            </div>
            <div className="flex items-center space-x-1">
              <EyeIcon className="w-4 h-4" />
              <span>{totalSignals}</span>
            </div>
          </div>
        </div>
        
        {/* Update info - separate line */}
        <div className="flex justify-end">
          <div className="text-xs text-gray-400">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{totalSignals}</div>
          <div className="text-xs text-gray-500">Total</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{buySignals}</div>
          <div className="text-xs text-gray-500">Buys</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">{sellSignals}</div>
          <div className="text-xs text-gray-500">Sells</div>
        </div>
      </div>

      {/* Signal List */}
      <div className="space-y-3">
        {data.slice(0, 4).map((signal, index) => (
          <div 
            key={signal.signal_id || index} 
            className="relative flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
            onMouseEnter={() => setHoveredSignal(signal)}
            onMouseLeave={() => setHoveredSignal(null)}
          >
            <div className="flex items-center space-x-3">
              {getSignalIcon(signal.direction)}
              <div>
                <div className="font-medium text-sm text-gray-900">{signal.symbol}</div>
                <div className="flex items-center space-x-2">
                  <div className="text-xs text-gray-500">{signal.direction}</div>
                  {(() => {
                    const status = getSignalStatus(signal);
                    return status ? (
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${status.color}`}>
                        {status.icon} {status.text}
                      </span>
                    ) : null;
                  })()}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(signal.confidence)}`}>
                {signal.confidence?.toFixed(1)}%
              </span>
              <div className="text-xs text-gray-500">
                ${signal.entry_price?.toFixed(2)}
              </div>
              <InformationCircleIcon className="w-4 h-4 text-gray-400" />
            </div>

            {/* Tooltip */}
            {hoveredSignal && hoveredSignal.signal_id === signal.signal_id && (
              <div className="absolute z-50 w-80 p-4 bg-white border border-gray-200 rounded-lg shadow-lg top-full left-0 mt-2">
                {formatTooltipContent(signal)}
              </div>
            )}
          </div>
        ))}
        
        {data.length > 4 && (
          <div className="text-center">
            <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
              See {data.length - 4} more
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <ClockIcon className="w-4 h-4" />
            <span>Last Update</span>
          </div>
          <span>Hace 2 min</span>
        </div>
      </div>
    </div>
  );
};

export default ActiveSignalsWidget;