"""
CoinCap Collector - Completely free API
"""
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_collector import BaseDataCollector

logger = logging.getLogger(__name__)

class CoinCapSource(BaseDataCollector):
    """CoinCap data source using free public endpoints"""
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.base_url = "https://api.coincap.io/v2"
        self.session = None
        
        # Symbol mapping (CoinCap uses different IDs)
        self.symbol_map = {
            'BTC-USD': 'bitcoin',
            'ETH-USD': 'ethereum', 
            'ADA-USD': 'cardano',
            'LTC-USD': 'litecoin',
            'LINK-USD': 'chainlink',
            'MATIC-USD': 'polygon',
            'SOL-USD': 'solana',
            'DOT-USD': 'polkadot'
        }
        
        # Store recent prices for indicators
        self.price_history = {}
        
        logger.info(f"🔧 CoinCapSource collector created")

    async def initialize(self) -> bool:
        """Initialize CoinCap connection"""
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
                logger.info("✅ CoinCap connection successful")
                return True
            else:
                logger.error("❌ CoinCap connection failed")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing CoinCap: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection to CoinCap"""
        try:
            test_url = f"{self.base_url}/assets"
            params = {'limit': 1}
            
            async with self.session.get(test_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('data'):
                        self.connection_status = True
                        logger.info("✅ CoinCap test successful")
                        return True
                return False
        except Exception as e:
            logger.error(f"❌ CoinCap connection test failed: {e}")
            return False

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        try:
            coin_id = self.symbol_map.get(symbol)
            if not coin_id:
                logger.error(f"❌ Symbol {symbol} not supported")
                return {}
            
            # Get asset data
            asset_url = f"{self.base_url}/assets/{coin_id}"
            
            async with self.session.get(asset_url) as response:
                if response.status == 200:
                    data = await response.json()
                    asset_data = data.get('data', {})
                    
                    current_price = float(asset_data.get('priceUsd', 0))
                    volume = float(asset_data.get('volumeUsd24Hr', 0))
                    change_24h = float(asset_data.get('changePercent24Hr', 0))
                    
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
        """Get historical data from stored prices"""
        try:
            if symbol not in self.price_history:
                logger.warning(f"⚠️ No price history for {symbol}")
                return None
            
            history = self.price_history[symbol]
            if len(history) < 10:
                logger.warning(f"⚠️ Insufficient price history for {symbol} ({len(history)} points)")
                return None
            
            # Convert stored prices to OHLCV format
            formatted_data = []
            for price_point in history[-limit:]:
                formatted_data.append({
                    'timestamp': price_point['timestamp'],
                    'close': price_point['price'],
                    'open': price_point['price'],  # Simple approximation
                    'high': price_point['price'],
                    'low': price_point['price'],
                    'volume': price_point['volume']
                })
            
            logger.info(f"✅ Returning {len(formatted_data)} historical points for {symbol}")
            return formatted_data
                    
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None

    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.session:
                await self.session.close()
            logger.info("🧹 CoinCapSource cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
