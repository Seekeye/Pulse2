import React, { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/react/24/outline';
import MiniChart from '../MiniChart';

const MarketOverviewWidget = ({ data = {} }) => {
  const symbols = Object.keys(data || {});
  const hasData = symbols.length > 0;
  const [priceHistory, setPriceHistory] = useState({});
  const [lastUpdate, setLastUpdate] = useState(new Date());

  // Fetch price history for each symbol (only once when symbols change)
  useEffect(() => {
    const fetchPriceHistory = async () => {
      const historyData = {};
      for (const symbol of symbols) {
        try {
          const response = await fetch(`http://localhost:8004/api/price-history/${symbol}?limit=10`);
          if (response.ok) {
            const data = await response.json();
            historyData[symbol] = data.prices;
          }
        } catch (error) {
          console.error(`Error fetching price history for ${symbol}:`, error);
        }
      }
      setPriceHistory(historyData);
      setLastUpdate(new Date());
    };

    if (hasData && symbols.length > 0) {
      fetchPriceHistory();
    }
  }, [symbols.join(',')]); // Only depend on symbols string, not the array reference

  const getChangeColor = (change) => {
    if (change > 0) return 'text-green-600';
    if (change < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getChangeIcon = (change) => {
    if (change > 0) return <ArrowUpIcon className="w-4 h-4 text-green-500" />;
    if (change < 0) return <ArrowDownIcon className="w-4 h-4 text-red-500" />;
    return <div className="w-4 h-4" />;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-3">
      <div className="mb-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <ChartBarIcon className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Market Overview</h3>
          </div>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Live</span>
            </div>
            <div className="flex items-center space-x-1">
              <ChartBarIcon className="w-4 h-4" />
              <span>{symbols.length} symbols</span>
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

      {/* Market Status */}
      <div className="mb-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">Market Status</div>
          <div className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-medium">
            {hasData ? 'Active' : 'No data'}
          </div>
        </div>
      </div>

      {/* Market Data */}
      <div className="space-y-3">
        {hasData ? (
          symbols.slice(0, 6).map((symbol) => {
            const price = data[symbol];
            const change = 0; // No tenemos datos de cambio reales
            return (
              <div key={symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                    <span className="text-xs font-medium text-gray-600">
                      {symbol.split('-')[0].substring(0, 3)}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-sm text-gray-900">{symbol}</div>
                    <div className="text-xs text-gray-500">Current price</div>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {/* Mini Chart */}
                  <MiniChart 
                    data={priceHistory[symbol] || []}
                    width={60}
                    height={30}
                    color={change >= 0 ? '#10B981' : '#EF4444'}
                    currentPrice={price}
                  />
                  <div className="text-right">
                    <div className="font-medium text-sm text-gray-900">${price?.toFixed(2) || '0.00'}</div>
                    <div className={`text-xs flex items-center space-x-1 ${getChangeColor(change)}`}>
                      {getChangeIcon(change)}
                      <span>{change > 0 ? '+' : ''}{change.toFixed(2)}%</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="text-center py-8 text-gray-500">
            <ChartBarIcon className="w-12 h-12 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">No market data</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MarketOverviewWidget;