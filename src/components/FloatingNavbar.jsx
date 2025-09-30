import React, { useState } from 'react';
import { 
  Bars3Icon, 
  BellIcon, 
  ExclamationTriangleIcon,
  ChartBarIcon,
  EyeIcon,
  Cog6ToothIcon,
  HomeIcon
} from '@heroicons/react/24/outline';

const FloatingNavbar = ({ onToggleSidebar, isConnected, activeTab, onTabChange }) => {
  const [isExpanded, setIsExpanded] = useState(false);

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

  return (
    <div 
      className="fixed bottom-4 right-4 z-50"
      onMouseEnter={() => setIsExpanded(true)}
      onMouseLeave={() => setIsExpanded(false)}
    >
      {/* Floating Button */}
      <div className="relative">
        {/* Expanded Menu */}
        <div className={`absolute bottom-16 right-0 transition-all duration-300 ${
          isExpanded ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'
        }`}>
          <div className="bg-dark-surface/95 backdrop-blur-sm rounded-2xl shadow-2xl border border-dark-border p-4 min-w-[200px]">
            {/* Connection Status */}
            <div className="mb-4 pb-4 border-b border-dark-border">
              <div className="flex items-center space-x-2">
                {isConnected ? (
                  <div className="flex items-center space-x-2 text-green-400">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium">Connected</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2 text-red-400">
                    <ExclamationTriangleIcon className="w-5 h-5" />
                    <span className="text-sm font-medium">Disconnected</span>
                  </div>
                )}
              </div>
            </div>

            {/* Navigation Links */}
            <nav className="space-y-2 mb-4 pb-4 border-b border-dark-border">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`flex items-center w-full p-2 rounded-lg text-sm font-medium transition-colors duration-200
                    ${activeTab === item.id ? 'bg-electric-blue/20 text-electric-blue' : 'text-gray-300 hover:bg-dark-border hover:text-white'}`}
                >
                  <item.icon className={`w-5 h-5 mr-3 ${activeTab === item.id ? 'text-electric-blue' : 'text-gray-400'}`} />
                  {item.name}
                </button>
              ))}
            </nav>

            {/* Notifications */}
            <div className="flex items-center justify-between text-sm text-gray-300">
              <div className="flex items-center space-x-2">
                <BellIcon className="w-5 h-5 text-gray-400" />
                <span>Notifications</span>
              </div>
              <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">3</span>
            </div>
          </div>
        </div>

        {/* Main Floating Button */}
        <button 
          className={`relative w-14 h-14 rounded-full shadow-lg flex items-center justify-center 
            bg-gradient-to-br from-electric-blue to-electric-blue-dark text-white text-2xl font-bold 
            hover:shadow-xl hover:shadow-electric-blue/25 transition-all duration-300 transform ${isExpanded ? 'rotate-45' : ''}`}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <Bars3Icon className={`w-7 h-7 transition-transform duration-300 ${isExpanded ? 'rotate-90' : ''}`} />
        </button>
      </div>
    </div>
  );
};

export default FloatingNavbar;