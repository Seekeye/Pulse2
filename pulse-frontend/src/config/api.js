// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8004';

export const API_ENDPOINTS = {
  DASHBOARD_DATA: `${API_BASE_URL}/api/dashboard-data`,
  TEST_PRICES: `${API_BASE_URL}/api/test-prices`,
  RESET_DATABASE: `${API_BASE_URL}/api/reset-database`,
  GENERATE_TEST_SIGNALS: `${API_BASE_URL}/api/generate-test-signals`,
  PRICE_HISTORY: (symbol, limit = 10) => `${API_BASE_URL}/api/price-history/${symbol}?limit=${limit}`,
};

export default API_BASE_URL;
