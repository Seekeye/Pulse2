import React from 'react';
import { 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  FlagIcon,
  ShieldExclamationIcon
} from '@heroicons/react/24/outline';

const TrackingEventsWidget = ({ data = [] }) => {
  const events = data || [];
  const hasData = events.length > 0;

  const getEventIcon = (eventType) => {
    switch (eventType) {
      case 'tp1_hit':
      case 'tp2_hit':
      case 'tp3_hit':
        return <CheckCircleIcon className="w-4 h-4 text-green-500" />;
      case 'stop_loss_hit':
        return <ShieldExclamationIcon className="w-4 h-4 text-red-500" />;
      case 'signal_closed':
        return <FlagIcon className="w-4 h-4 text-blue-500" />;
      default:
        return <ExclamationTriangleIcon className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getEventColor = (eventType) => {
    switch (eventType) {
      case 'tp1_hit':
      case 'tp2_hit':
      case 'tp3_hit':
        return 'text-green-600 bg-green-50';
      case 'stop_loss_hit':
        return 'text-red-600 bg-red-50';
      case 'signal_closed':
        return 'text-blue-600 bg-blue-50';
      default:
        return 'text-yellow-600 bg-yellow-50';
    }
  };

  const formatEventType = (eventType) => {
    switch (eventType) {
      case 'tp1_hit': return 'TP1 Hit';
      case 'tp2_hit': return 'TP2 Hit';
      case 'tp3_hit': return 'TP3 Hit';
      case 'stop_loss_hit': return 'Stop Loss';
      case 'signal_closed': return 'Signal Closed';
      case 'signal_reinforced': return 'Signal Reinforced';
      case 'signal_conflicted': return 'Conflict';
      case 'signal_replaced': return 'Signal Replaced';
      default: return eventType;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-3">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          <FlagIcon className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Tracking Events</h3>
        </div>
        <div className="flex items-center space-x-1 text-sm text-gray-500">
          <FlagIcon className="w-4 h-4" />
          <span>{events.length}</span>
        </div>
      </div>

      {/* Events List */}
      <div className="space-y-3">
        {hasData ? (
          events.slice(0, 5).map((event, index) => (
            <div key={event.id || index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
              <div className="flex-shrink-0 mt-0.5">
                {getEventIcon(event.event_type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm text-gray-900">{event.symbol}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getEventColor(event.event_type)}`}>
                      {formatEventType(event.event_type)}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </div>
                </div>
                <div className="mt-1 text-sm text-gray-600">
                  {event.message || `${event.symbol} - ${formatEventType(event.event_type)}`}
                </div>
                <div className="mt-1 text-xs text-gray-500">
                  Price: ${event.current_price?.toFixed(4)} | P&L: {event.profit_loss_pct?.toFixed(2)}%
                </div>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-8 text-gray-500">
            <FlagIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">No tracking events</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrackingEventsWidget;