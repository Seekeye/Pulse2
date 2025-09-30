import React from 'react';
import { 
  Bars3Icon, 
  BellIcon, 
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const Header = ({ onToggleSidebar, sidebarCollapsed, isConnected, activeTab = 'dashboard' }) => {

  return (
    <header className="bg-dark-surface border-b border-dark-border px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left Side */}
        <div className="flex items-center space-x-4">
          <button
            onClick={onToggleSidebar}
            className="p-2 text-gray-400 hover:text-electric-blue hover:bg-dark-border rounded-lg transition-colors"
          >
            <Bars3Icon className="w-5 h-5" />
          </button>
          
          <div>
            <h1 className="text-2xl font-bold text-white capitalize">{activeTab}</h1>
            <p className="text-sm text-gray-400">Intelligent Technical Analysis System</p>
          </div>
        </div>

        {/* Right Side */}
        <div className="flex items-center space-x-4">
          {/* Connection Status */}
          <div className="flex items-center space-x-2">
            {isConnected ? (
              <div className="flex items-center space-x-2 text-green-400">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">Connected</span>
              </div>
            ) : (
              <div className="flex items-center space-x-2 text-red-400">
                <ExclamationTriangleIcon className="w-4 h-4" />
                <span className="text-sm font-medium">Disconnected</span>
              </div>
            )}
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-gray-400 hover:text-electric-blue hover:bg-dark-border rounded-lg transition-colors">
            <BellIcon className="w-5 h-5" />
            <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              3
            </span>
          </button>

          {/* User Profile */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">U</span>
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900">User</p>
              <p className="text-xs text-gray-500">Trading Analyst</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;