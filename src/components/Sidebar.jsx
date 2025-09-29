import React, { useState } from 'react';
import { 
  HomeIcon, 
  ChartBarIcon, 
  EyeIcon, 
  Cog6ToothIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CurrencyDollarIcon,
  TrashIcon,
  ArrowPathIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { API_ENDPOINTS } from '../config/api';
import logoImage from '../assets/logo.webp';

const Sidebar = ({ collapsed, activeTab, onTabChange, onDataRefresh }) => {
  const [isResetting, setIsResetting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [showControls, setShowControls] = useState(false);
  const menuItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      icon: HomeIcon,
      color: 'blue'
    },
    {
      id: 'signals',
      name: 'Signals',
      icon: ChartBarIcon,
      color: 'green'
    },
    {
      id: 'tracking',
      name: 'Tracking',
      icon: EyeIcon,
      color: 'purple'
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: Cog6ToothIcon,
      color: 'gray'
    }
  ];

  // System control functions
  const handleResetDatabase = async () => {
    if (!showConfirm) {
      setShowConfirm(true);
      return;
    }

    setIsResetting(true);
    try {
      const response = await fetch(API_ENDPOINTS.RESET_DATABASE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Database reset successfully:', result);
        
        if (onDataRefresh) {
          onDataRefresh();
        }
        
        alert('✅ Base de datos reseteada exitosamente');
      } else {
        throw new Error('Failed to reset database');
      }
    } catch (error) {
      console.error('❌ Error resetting database:', error);
      alert('❌ Error al resetear la base de datos');
    } finally {
      setIsResetting(false);
      setShowConfirm(false);
    }
  };

  const handleRefreshData = () => {
    if (onDataRefresh) {
      onDataRefresh();
    }
  };

  const handleGenerateTestSignals = async () => {
    setIsGenerating(true);
    try {
      const response = await fetch(API_ENDPOINTS.GENERATE_TEST_SIGNALS, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Test signals generated successfully:', result);
        
        if (onDataRefresh) {
          onDataRefresh();
        }
        
        alert('✅ Señales de prueba generadas exitosamente');
      } else {
        throw new Error('Failed to generate test signals');
      }
    } catch (error) {
      console.error('❌ Error generating test signals:', error);
      alert('❌ Error al generar señales de prueba');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className={`bg-gradient-to-b from-slate-900 via-gray-900 to-slate-800 border-r border-slate-700/30 transition-all duration-300 flex flex-col h-full shadow-2xl ${
      collapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Header */}
      <div className="p-6 border-b border-slate-700/30 bg-gradient-to-r from-slate-800/50 to-transparent">
        <div className="flex items-center space-x-3">
          <div className={`${collapsed ? 'w-14 h-14 -ml-2' : 'w-10 h-10'} rounded-xl flex items-center justify-center shadow-lg ring-2 ring-blue-500/20 overflow-hidden transition-all duration-300`}>
            <img 
              src={logoImage} 
              alt="Pulse Logo" 
              className="w-full h-full object-cover rounded-xl"
            />
          </div>
          {!collapsed && (
            <div>
              <h1 className="text-xl font-bold text-gray-800">Pulse</h1>
              <p className="text-xs text-gray-800">Trading Signals</p>
            </div>
          )}
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-2 flex-1">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`group w-full flex items-center ${collapsed ? 'justify-center px-2 py-4' : 'space-x-3 px-3 py-3'} rounded-lg text-sm font-medium transition-all duration-200 ${
              activeTab === item.id
                ? `bg-gradient-to-r from-${item.color}-500/20 to-${item.color}-600/10 text-${item.color}-300 border border-${item.color}-400/30 shadow-lg ring-1 ring-${item.color}-400/20`
                : 'text-gray-900 hover:bg-slate-800/50 hover:text-gray-900 hover:shadow-md'
            }`}
          >
            <item.icon className={`${collapsed ? 'w-10 h-10' : 'w-5 h-5'} transition-all duration-200 ${
              activeTab === item.id ? `text-${item.color}-400` : 'text-gray-900 group-hover:text-gray-900'
            }`} />
            {!collapsed && <span>{item.name}</span>}
          </button>
        ))}
      </nav>

      {/* System Controls Section */}
      <div className="mt-auto p-3 border-t border-slate-700/30 bg-gradient-to-t from-slate-800/30 to-transparent">
        {/* Controls Toggle Button */}
        <button
          onClick={() => setShowControls(!showControls)}
          className="w-full flex items-center justify-between p-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 transition-all duration-200 mb-2 border border-slate-700/30 hover:border-slate-600/50"
        >
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            {!collapsed && <span className="text-xs font-medium text-gray-800">System Control</span>}
          </div>
          <Cog6ToothIcon className={`${collapsed ? 'w-6 h-6' : 'w-5 h-5'} text-gray-800 transition-all duration-200 ${showControls ? 'rotate-180' : ''}`} />
        </button>

        {/* Controls Panel */}
        {showControls && !collapsed && (
          <div className="space-y-2 animate-in slide-in-from-top-2 duration-300">
            {/* Status */}
            <div className="flex items-center justify-between text-xs px-2">
              <span className="text-gray-800">Status:</span>
              <span className="text-green-400 font-medium">Online</span>
            </div>

            {/* Control Buttons */}
            <div className="space-y-1.5">
              {/* Refresh Button */}
              <button
                onClick={handleRefreshData}
                className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-gradient-to-r from-blue-500/20 to-cyan-500/10 text-blue-300 rounded-lg hover:from-blue-500/30 hover:to-cyan-500/20 transition-all duration-200 text-xs font-medium border border-blue-500/30 hover:border-blue-400/50 shadow-md hover:shadow-lg"
              >
                <ArrowPathIcon className="w-3 h-3" />
                <span>Refresh Data</span>
              </button>

              {/* Generate Test Signals Button */}
              <button
                onClick={handleGenerateTestSignals}
                disabled={isGenerating}
                className={`w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-xs font-medium border ${
                  isGenerating 
                    ? 'bg-slate-500/20 text-slate-500 border-slate-600/30 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-green-500/20 to-emerald-500/10 text-green-300 border-green-500/30 hover:from-green-500/30 hover:to-emerald-500/20 hover:border-green-400/50 shadow-md hover:shadow-lg'
                }`}
              >
                {isGenerating ? (
                  <>
                    <ArrowPathIcon className="w-3 h-3 animate-spin" />
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <ArrowPathIcon className="w-3 h-3" />
                    <span>Test Data</span>
                  </>
                )}
              </button>

              {/* Reset Database Button */}
              <button
                onClick={handleResetDatabase}
                disabled={isResetting}
                className={`w-full flex items-center justify-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 text-xs font-medium border ${
                  showConfirm
                    ? 'bg-gradient-to-r from-red-500/20 to-rose-500/10 text-red-300 border-red-500/30 hover:from-red-500/30 hover:to-rose-500/20 shadow-md hover:shadow-lg'
                    : 'bg-gradient-to-r from-orange-500/20 to-amber-500/10 text-orange-300 border-orange-500/30 hover:from-orange-500/30 hover:to-amber-500/20 shadow-md hover:shadow-lg'
                } ${isResetting ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                {isResetting ? (
                  <>
                    <ArrowPathIcon className="w-3 h-3 animate-spin" />
                    <span>Resetting...</span>
                  </>
                ) : showConfirm ? (
                  <>
                    <ExclamationTriangleIcon className="w-3 h-3" />
                    <span>Confirm Reset?</span>
                  </>
                ) : (
                  <>
                    <TrashIcon className="w-3 h-3" />
                    <span>Reset Database</span>
                  </>
                )}
              </button>
            </div>

            {/* Warning for Reset */}
            {showConfirm && (
              <div className="text-xs text-yellow-400 bg-gradient-to-r from-yellow-500/10 to-amber-500/5 p-2 rounded border border-yellow-500/20 shadow-md">
                ⚠️ This will delete ALL data
              </div>
            )}
          </div>
        )}

        {/* Collapsed Controls */}
        {collapsed && (
          <div className="space-y-1">
            <button
              onClick={handleRefreshData}
              className="w-full p-2 bg-gradient-to-r from-blue-500/20 to-cyan-500/10 text-blue-300 rounded-lg hover:from-blue-500/30 hover:to-cyan-500/20 transition-all duration-200 shadow-md hover:shadow-lg"
              title="Refresh Data"
            >
              <ArrowPathIcon className="w-6 h-6 mx-auto" />
            </button>
            <button
              onClick={handleGenerateTestSignals}
              disabled={isGenerating}
              className={`w-full p-2 rounded-lg transition-all duration-200 ${
                isGenerating 
                  ? 'bg-slate-500/20 text-slate-500 cursor-not-allowed' 
                  : 'bg-gradient-to-r from-green-500/20 to-emerald-500/10 text-green-300 hover:from-green-500/30 hover:to-emerald-500/20 shadow-md hover:shadow-lg'
              }`}
              title="Generate Test Data"
            >
              {isGenerating ? (
                <ArrowPathIcon className="w-6 h-6 mx-auto animate-spin" />
              ) : (
                <ArrowPathIcon className="w-6 h-6 mx-auto" />
              )}
            </button>
            <button
              onClick={handleResetDatabase}
              disabled={isResetting}
              className={`w-full p-2 rounded-lg transition-all duration-200 ${
                showConfirm
                  ? 'bg-gradient-to-r from-red-500/20 to-rose-500/10 text-red-300 hover:from-red-500/30 hover:to-rose-500/20 shadow-md hover:shadow-lg'
                  : 'bg-gradient-to-r from-orange-500/20 to-amber-500/10 text-orange-300 hover:from-orange-500/30 hover:to-amber-500/20 shadow-md hover:shadow-lg'
              } ${isResetting ? 'opacity-50 cursor-not-allowed' : ''}`}
              title="Reset Database"
            >
              {isResetting ? (
                <ArrowPathIcon className="w-6 h-6 mx-auto animate-spin" />
              ) : showConfirm ? (
                <ExclamationTriangleIcon className="w-6 h-6 mx-auto" />
              ) : (
                <TrashIcon className="w-6 h-6 mx-auto" />
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;