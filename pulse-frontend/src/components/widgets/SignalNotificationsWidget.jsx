import React, { useState, useEffect } from 'react';
import { 
  ExclamationTriangleIcon,
  HandThumbUpIcon,
  ArrowPathIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

const SignalNotificationsWidget = ({ data = [] }) => {
  const [notifications, setNotifications] = useState([]);
  const [expandedNotification, setExpandedNotification] = useState(null);

  // Update notifications when data changes
  useEffect(() => {
    if (data && data.length > 0) {
      setNotifications(data);
    }
  }, [data]);

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'SIGNAL_REINFORCED':
        return <HandThumbUpIcon className="w-5 h-5 text-blue-500" />;
      case 'SIGNAL_CONFLICTED':
        return <ExclamationTriangleIcon className="w-5 h-5 text-orange-500" />;
      case 'SIGNAL_REPLACED':
        return <ArrowPathIcon className="w-5 h-5 text-purple-500" />;
      default:
        return <ExclamationTriangleIcon className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationColor = (type) => {
    switch (type) {
      case 'SIGNAL_REINFORCED':
        return 'bg-blue-50 border-blue-200';
      case 'SIGNAL_CONFLICTED':
        return 'bg-orange-50 border-orange-200';
      case 'SIGNAL_REPLACED':
        return 'bg-purple-50 border-purple-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const getNotificationTitle = (type) => {
    switch (type) {
      case 'SIGNAL_REINFORCED':
        return 'Señal Reforzada';
      case 'SIGNAL_CONFLICTED':
        return 'Conflicto Detectado';
      case 'SIGNAL_REPLACED':
        return 'Señal Reemplazada';
      default:
        return 'Evento de Señal';
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const dismissNotification = (index) => {
    setNotifications(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <ExclamationTriangleIcon className="w-5 h-5 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-900">Notificaciones de Señales</h3>
        </div>
        <div className="text-sm text-gray-500">
          {notifications.length} eventos
        </div>
      </div>

      <div className="space-y-3 max-h-80 overflow-y-auto">
        {notifications.length > 0 ? (
          notifications.slice(0, 10).map((notification, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getNotificationColor(notification.event)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getNotificationIcon(notification.event)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="font-medium text-sm text-gray-900">
                        {getNotificationTitle(notification.event)}
                      </h4>
                      <span className="text-xs text-gray-500">
                        {formatTimestamp(notification.timestamp)}
                      </span>
                    </div>
                    
                    <div className="text-sm text-gray-700 mb-2">
                      <div className="font-medium">{notification.symbol}</div>
                      <div className="text-xs text-gray-600">{notification.message}</div>
                    </div>

                    <div className="flex items-center space-x-4 text-xs text-gray-600">
                      <div>
                        <span className="font-medium">Precio:</span> ${notification.current_price?.toFixed(4)}
                      </div>
                      <div>
                        <span className="font-medium">P&L:</span> {notification.profit_loss_pct?.toFixed(2)}%
                      </div>
                    </div>

                    {/* Expand button for more details */}
                    <button
                      onClick={() => setExpandedNotification(
                        expandedNotification === index ? null : index
                      )}
                      className="mt-2 text-xs text-blue-600 hover:text-blue-800 font-medium"
                    >
                      {expandedNotification === index ? 'Menos detalles' : 'Más detalles'}
                    </button>

                    {/* Expanded details */}
                    {expandedNotification === index && (
                      <div className="mt-3 p-3 bg-white rounded border text-xs">
                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <span className="font-medium text-gray-600">ID de Señal:</span>
                            <div className="text-gray-800 font-mono">{notification.signal_id}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Precio Objetivo:</span>
                            <div className="text-gray-800">${notification.target_price?.toFixed(4)}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Evento:</span>
                            <div className="text-gray-800">{notification.event}</div>
                          </div>
                          <div>
                            <span className="font-medium text-gray-600">Timestamp:</span>
                            <div className="text-gray-800">{new Date(notification.timestamp).toLocaleString()}</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => dismissNotification(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center text-gray-500 py-8">
            <ExclamationTriangleIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p>No hay notificaciones recientes</p>
          </div>
        )}
      </div>

      {notifications.length > 10 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800 font-medium">
            Ver {notifications.length - 10} notificaciones más
          </button>
        </div>
      )}
    </div>
  );
};

export default SignalNotificationsWidget;
