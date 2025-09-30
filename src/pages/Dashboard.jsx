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

  // WebSocket connection for real-time data
  const { data: wsData, isConnected } = useWebSocket('ws://localhost:8000/ws');

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

  useEffect(() => {
    if (wsData) {
      setDashboardData(prev => ({
        ...prev,
        ...wsData
      }));
    }
  }, [wsData]);

  // Fetch data on component mount and every 10 seconds for real-time updates
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 10000); // 10 seconds instead of 30

    return () => clearInterval(interval);
  }, []);

  const toggleSidebar = () => {
    setSidebarCollapsed(!sidebarCollapsed);
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      {/* Test styles */}
      <div className="bg-electric-blue text-white p-4 m-4 rounded-lg">
        <h1 className="text-2xl font-bold">Test: Estilos funcionando</h1>
        <p className="text-sm">Si ves este mensaje con fondo azul, los estilos están funcionando</p>
      </div>
      
      {/* Sidebar */}
      <Sidebar 
        collapsed={sidebarCollapsed} 
        activeTab={activeTab} 
        onTabChange={setActiveTab}
      />

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarCollapsed ? 'ml-16' : 'ml-64'}`}>
        {/* Header */}
        <Header 
          onToggleSidebar={toggleSidebar}
          sidebarCollapsed={sidebarCollapsed}
        />

        {/* Floating Navbar */}
        <FloatingNavbar 
          activeTab={activeTab} 
          onTabChange={setActiveTab}
        />

        {/* Dashboard Content */}
        <div className="p-4 pt-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {/* Market Overview */}
            <div className="lg:col-span-2 xl:col-span-1">
              <MarketOverviewWidget 
                marketData={dashboardData.marketData}
                onRefresh={fetchDashboardData}
              />
            </div>

            {/* Active Signals */}
            <div className="lg:col-span-1 xl:col-span-1">
              <ActiveSignalsWidget 
                signals={dashboardData.activeSignals}
                onRefresh={fetchDashboardData}
              />
            </div>

            {/* Performance */}
            <div className="lg:col-span-1 xl:col-span-1">
              <PerformanceWidget 
                performance={dashboardData.performance}
              />
            </div>

            {/* Indicators */}
            <div className="lg:col-span-2 xl:col-span-1">
              <IndicatorsWidget 
                marketData={dashboardData.marketData}
              />
            </div>

            {/* Tracking Events */}
            <div className="lg:col-span-1 xl:col-span-1">
              <TrackingEventsWidget 
                events={dashboardData.trackingEvents}
              />
            </div>

            {/* Recent Signals */}
            <div className="lg:col-span-1 xl:col-span-1">
              <RecentSignalsWidget 
                signals={dashboardData.recentSignals}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
