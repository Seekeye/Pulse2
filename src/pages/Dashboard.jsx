import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import FloatingNavbar from '../components/FloatingNavbar';
import ActiveSignalsWidget from '../components/widgets/ActiveSignalsWidget';
import MarketOverviewWidget from '../components/widgets/MarketOverviewWidget';
import IndicatorsWidget from '../components/widgets/IndicatorsWidget';
import TrackingEventsWidget from '../components/widgets/TrackingEventsWidget';
import PerformanceWidget from '../components/widgets/PerformanceWidget';
import RecentSignalsWidget from '../components/widgets/RecentSignalsWidget';
import { useWebSocket } from '../hooks/useWebSocket';
import { API_ENDPOINTS } from '../config/api';

const Dashboard = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [dashboardData, setDashboardData] = useState({
    activeSignals: [],
    marketData: {},
    trackingEvents: [],
    performance: {},
    recentSignals: []
  });

  // WebSocket connection for real-time data (disabled for now)
  // const { data: wsData, isConnected } = useWebSocket('wss://pulse-xxfq.onrender.com/ws');

  // Fetch data from API
  const fetchDashboardData = async () => {
    try {
      console.log('🔄 Fetching dashboard data from API...');
      const response = await fetch(API_ENDPOINTS.DASHBOARD_DATA);
      console.log('📡 API Response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Dashboard data received:', data);
        setDashboardData(data);
      } else {
        console.error('❌ API Error:', response.status, response.statusText);
      }
    } catch (error) {
      console.error('❌ Error fetching dashboard data:', error);
    }
  };

  // useEffect(() => {
  //   if (wsData) {
  //     setDashboardData(prev => ({
  //       ...prev,
  //       ...wsData
  //     }));
  //   }
  // }, [wsData]);

  // Fetch data on component mount and every 10 seconds for real-time updates
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // 10 seconds instead of 30
    return () => clearInterval(interval);
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  // ... existing code ...

  const renderDashboardContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <div className="space-y-6 w-full">
            {/* Header Row */}
            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 w-full">
              <ActiveSignalsWidget data={dashboardData.activeSignals} />
              <MarketOverviewWidget data={dashboardData.marketData} />
              <PerformanceWidget data={dashboardData.performance} />
            </div>

            {/* Middle Row */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 w-full">
              <IndicatorsWidget data={dashboardData.marketData} />
              <TrackingEventsWidget data={dashboardData.trackingEvents} />
            </div>



            {/* Bottom Row */}
            <div className="grid grid-cols-1 gap-6 w-full">
              <RecentSignalsWidget data={dashboardData.recentSignals} />
            </div>
          </div>
        );
      case 'signals':
        return <div>Signals Management</div>;
      case 'tracking':
        return <div>Signal Tracking</div>;
      case 'settings':
        return <div>Settings</div>;
      default:
        return <div>Dashboard</div>;
    }
  };

  // ... existing code ...

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${sidebarCollapsed ? 'w-16' : 'w-64'} transition-all duration-300`}>
        <Sidebar 
          collapsed={sidebarCollapsed} 
          activeTab={activeTab} 
          onTabChange={setActiveTab}
          onDataRefresh={fetchDashboardData}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <Header 
          onToggleSidebar={toggleSidebar}
          isConnected={isConnected}
          activeTab={activeTab}
        />

        {/* Dashboard Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="w-full">
            {renderDashboardContent()}
          </div>
        </main>
      </div>

      {/* Floating Navbar - Bottom Right */}
      <FloatingNavbar 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
        isConnected={isConnected}
      />
    </div>
  );

// ... existing code ...
}

export default Dashboard;
