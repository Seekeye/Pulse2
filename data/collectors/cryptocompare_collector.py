"""
CryptoCompare Collector - Free tier API
"""
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_collector import BaseDataCollector

logger = logging.getLogger(__name__)

class CryptoCompareSource(BaseDataCollector):
    """CryptoCompare data source using free tier"""
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.base_url = "https://min-api.cryptocompare.com/data"
        self.session = None
        
        # Symbol mapping (CryptoCompare uses different format)
        self.symbol_map = {
            'BTC-USD': 'BTC',
            'ETH-USD': 'ETH', 
            'ADA-USD': 'ADA',
            'LTC-USD': 'LTC',
            'LINK-USD': 'LINK',
            'MATIC-USD': 'MATIC',
            'SOL-USD': 'SOL',
            'DOT-USD': 'DOT'
        }
        
        # Store recent prices for indicators
        self.price_history = {}
        
        logger.info(f"🔧 CryptoCompareSource collector created")

    async def initialize(self) -> bool:
        """Initialize CryptoCompare connection"""
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
                logger.info("✅ CryptoCompare connection successful")
                return True
            else:
                logger.error("❌ CryptoCompare connection failed")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing CryptoCompare: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection to CryptoCompare"""
        try:
            test_url = f"{self.base_url}/ping"
            
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'Success':
                        self.connection_status = True
                        logger.info("✅ CryptoCompare test successful")
                        return True
                return False
        except Exception as e:
            logger.error(f"❌ CryptoCompare connection test failed: {e}")
            return False

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        try:
            coin_symbol = self.symbol_map.get(symbol)
            if not coin_symbol:
                logger.error(f"❌ Symbol {symbol} not supported")
                return {}
            
            # Get price data
            price_url = f"{self.base_url}/price"
            params = {
                'fsym': coin_symbol,
                'tsyms': 'USD'
            }
            
            # Get 24hr stats
            stats_url = f"{self.base_url}/pricemultifull"
            stats_params = {
                'fsyms': coin_symbol,
                'tsyms': 'USD'
            }
            
            # Make both requests
            price_response = await self.session.get(price_url, params=params)
            stats_response = await self.session.get(stats_url, params=stats_params)
            
            if price_response.status == 200 and stats_response.status == 200:
                price_data = await price_response.json()
                stats_data = await stats_response.json()
                
                current_price = float(price_data.get('USD', 0))
                
                # Extract stats
                raw_data = stats_data.get('RAW', {}).get(coin_symbol, {}).get('USD', {})
                volume = float(raw_data.get('TOTALVOLUME24H', 0))
                change_24h = float(raw_data.get('CHANGEPCT24HOUR', 0))
                
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
                logger.error(f"❌ Error fetching {symbol}: Price={price_response.status}, Stats={stats_response.status}")
                return {}
                    
        except Exception as e:
            logger.error(f"❌ Error getting data for {symbol}: {e}")
            return {}

    async def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[List]:
        """Get historical data from CryptoCompare"""
        try:
            coin_symbol = self.symbol_map.get(symbol)
            if not coin_symbol:
                logger.warning(f"⚠️ Symbol {symbol} not supported")
                return None
            
            # Map timeframe to CryptoCompare intervals
            interval_map = {
                "1m": "1m",
                "5m": "5m", 
                "15m": "15m",
                "1h": "1h",
                "4h": "4h",
                "1d": "1d"
            }
            
            interval = interval_map.get(timeframe, "1h")
            
            hist_url = f"{self.base_url}/v2/histohour"
            params = {
                'fsym': coin_symbol,
                'tsym': 'USD',
                'limit': min(limit, 2000),  # CryptoCompare max is 2000
                'aggregate': 1
            }
            
            async with self.session.get(hist_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('Response') == 'Success':
                        hist_data = data.get('Data', {}).get('Data', [])
                        
                        formatted_data = []
                        for candle in hist_data:
                            formatted_data.append({
                                'timestamp': candle['time'],
                                'open': float(candle['open']),
                                'high': float(candle['high']),
                                'low': float(candle['low']),
                                'close': float(candle['close']),
                                'volume': float(candle['volumeto'])
                            })
                        
                        logger.info(f"✅ Retrieved {len(formatted_data)} historical points for {symbol}")
                        return formatted_data
                    else:
                        logger.error(f"❌ CryptoCompare API error: {data.get('Message', 'Unknown error')}")
                        return None
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
            logger.info("🧹 CryptoCompareSource cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
