"""
Binance Collector - Free API without API key for basic data
"""
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_collector import BaseDataCollector

logger = logging.getLogger(__name__)

class BinanceSource(BaseDataCollector):
    """Binance data source using free public endpoints"""
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.base_url = "https://api.binance.com/api/v3"
        self.session = None
        
        # Symbol mapping (Binance uses USDT pairs)
        self.symbol_map = {
            'BTC-USD': 'BTCUSDT',
            'ETH-USD': 'ETHUSDT', 
            'ADA-USD': 'ADAUSDT',
            'LTC-USD': 'LTCUSDT',
            'LINK-USD': 'LINKUSDT',
            'MATIC-USD': 'MATICUSDT',
            'SOL-USD': 'SOLUSDT',
            'DOT-USD': 'DOTUSDT'
        }
        
        # Store recent prices for indicators
        self.price_history = {}
        
        logger.info(f"🔧 BinanceSource collector created")

    async def initialize(self) -> bool:
        """Initialize Binance connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'ChainPulse/1.0',
                    'Accept': 'application/json'
                }
            )
            
            if await self.test_connection():
                self.is_initialized = True
                logger.info("✅ Binance connection successful")
                return True
            else:
                logger.error("❌ Binance connection failed")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing Binance: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection to Binance"""
        try:
            test_url = f"{self.base_url}/ping"
            
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    self.connection_status = True
                    logger.info("✅ Binance test successful")
                    return True
                else:
                    logger.warning(f"⚠️ Binance test returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Binance connection test failed: {e}")
            return False

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        try:
            binance_symbol = self.symbol_map.get(symbol)
            if not binance_symbol:
                logger.error(f"❌ Symbol {symbol} not supported")
                return {}
            
            # Get 24hr ticker data (includes price, volume, change)
            ticker_url = f"{self.base_url}/ticker/24hr"
            params = {'symbol': binance_symbol}
            
            async with self.session.get(ticker_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    current_price = float(data.get('lastPrice', 0))
                    volume = float(data.get('volume', 0))
                    change_24h = float(data.get('priceChangePercent', 0))
                    
                    # Store price in history for indicators
                    if symbol not in self.price_history:
                        self.price_history[symbol] = []
                    
                    self.price_history[symbol].append({
                        'price': current_price,
                        'timestamp': int(time.time()),
                        'volume': volume
                    })
                    
                    # Keep only last 200 prices
                    if len(self.price_history[symbol]) > 200:
                        self.price_history[symbol] = self.price_history[symbol][-200:]
                    
                    return {
                        'symbol': symbol,
                        'price': current_price,
                        'volume': volume,
                        'change_24h': change_24h,
                        'timestamp': int(time.time()),
                        'last_updated': int(time.time())
                    }
                else:
                    logger.error(f"❌ Error fetching {symbol}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error getting data for {symbol}: {e}")
            return {}

    async def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[List]:
        """Get historical data from Binance"""
        try:
            binance_symbol = self.symbol_map.get(symbol)
            if not binance_symbol:
                logger.warning(f"⚠️ Symbol {symbol} not supported")
                return None
            
            # Map timeframe to Binance intervals
            interval_map = {
                "1m": "1m",
                "5m": "5m", 
                "15m": "15m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d"
            }
            
            interval = interval_map.get(timeframe, "1h")
            
            klines_url = f"{self.base_url}/klines"
            params = {
                'symbol': binance_symbol,
                'interval': interval,
                'limit': min(limit, 1000)  # Binance max is 1000
            }
            
            async with self.session.get(klines_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    formatted_data = []
                    for kline in data:
                        formatted_data.append({
                            'timestamp': kline[0] // 1000,  # Convert to seconds
                            'open': float(kline[1]),
                            'high': float(kline[2]),
                            'low': float(kline[3]),
                            'close': float(kline[4]),
                            'volume': float(kline[5])
                        })
                    
                    logger.info(f"✅ Retrieved {len(formatted_data)} historical points for {symbol}")
                    return formatted_data
                else:
                    logger.error(f"❌ Error fetching historical data for {symbol}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("🧹 BinanceSource cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")