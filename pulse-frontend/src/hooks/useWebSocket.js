import { useState, useEffect } from 'react'
import { API_ENDPOINTS } from '../config/api'

export const useWebSocket = (url) => {
  const [data, setData] = useState(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    // Load real data from backend API
    const loadRealData = async () => {
      try {
        console.log('🔄 Loading real data from backend...');
        const response = await fetch(API_ENDPOINTS.DASHBOARD_DATA, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const realData = await response.json();
          setData(realData);
          setIsConnected(true);
          console.log('✅ Real data loaded from backend:', realData);
        } else {
          console.log('❌ Backend error:', response.status);
          setIsConnected(false);
        }
      } catch (error) {
        console.log('❌ Backend not available:', error.message);
        setIsConnected(false);
      }
    };

    // Load data immediately
    loadRealData();

    // Load real data periodically every 5 seconds
    const interval = setInterval(async () => {
      try {
        const response = await fetch(API_ENDPOINTS.DASHBOARD_DATA, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (response.ok) {
          const realData = await response.json();
          setData(realData);
          setIsConnected(true);
          console.log('🔄 Real data updated from backend');
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        console.log('⚠️ Failed to update real data:', error.message);
        setIsConnected(false);
      }
    }, 5000);

    return () => {
      clearInterval(interval);
    }
  }, [])

  return { data, isConnected }
}

export default useWebSocket