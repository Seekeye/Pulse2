"""
CoinGecko Simple Collector - Uses only free endpoints
"""
import logging
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_collector import BaseDataCollector

logger = logging.getLogger(__name__)

class CoinGeckoSimpleSource(BaseDataCollector):
    """CoinGecko simple data source using only free endpoints"""
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
        # Symbol mapping
        self.symbol_map = {
            'BTC-USD': 'bitcoin',
            'ETH-USD': 'ethereum', 
            'ADA-USD': 'cardano',
            'LTC-USD': 'litecoin',
            'LINK-USD': 'chainlink',
            'MATIC-USD': 'matic-network',
            'SOL-USD': 'solana',
            'DOT-USD': 'polkadot'
        }
        
        # Store recent prices for simple indicators
        self.price_history = {}
        
        logger.info(f"🔧 CoinGeckoSimpleSource collector created")

    async def initialize(self) -> bool:
        """Initialize CoinGecko connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'ChainPulse/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Wait a bit before testing connection to avoid rate limits
            logger.info("⏳ Waiting before testing CoinGecko connection...")
            await asyncio.sleep(5)
            
            # Try connection test with retries
            max_connection_attempts = 3
            for attempt in range(max_connection_attempts):
                logger.info(f"🔗 Testing CoinGecko connection (attempt {attempt + 1}/{max_connection_attempts})...")
                
                if await self.test_connection():
                    self.is_initialized = True
                    logger.info("✅ CoinGecko Simple connection successful")
                    return True
                else:
                    if attempt < max_connection_attempts - 1:
                        wait_time = (attempt + 1) * 10  # 10, 20 seconds
                        logger.warning(f"⚠️ Connection test failed, waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error("❌ CoinGecko Simple connection failed after all attempts")
                        return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing CoinGecko Simple: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection to CoinGecko"""
        try:
            test_url = f"{self.base_url}/ping"
            
            # Add delay before test to avoid rate limits
            await asyncio.sleep(2)
            
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'gecko_says' in data:
                        self.connection_status = True
                        logger.info(f"✅ CoinGecko Simple test successful - {data['gecko_says']}")
                        return True
                elif response.status == 429:
                    logger.warning("⚠️ CoinGecko rate limit exceeded - waiting before retry")
                    await asyncio.sleep(10)  # Wait 10 seconds before retry
                    return False
                else:
                    logger.warning(f"⚠️ CoinGecko test returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            return False

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        try:
            coin_id = self.symbol_map.get(symbol)
            if not coin_id:
                logger.error(f"❌ Symbol {symbol} not supported")
                return {}
            
            # Add longer delay to avoid rate limits
            await asyncio.sleep(3)
            
            price_url = f"{self.base_url}/simple/price"
            params = {
                'ids': coin_id,
                'vs_currencies': 'usd',
                'include_24hr_vol': 'true',
                'include_24hr_change': 'true',
                'include_last_updated_at': 'true'
            }
            
            # Retry mechanism for rate limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    async with self.session.get(price_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            if coin_id in data:
                                coin_data = data[coin_id]
                                current_price = float(coin_data.get('usd', 0))
                                
                                # Store price in history for simple indicators
                                if symbol not in self.price_history:
                                    self.price_history[symbol] = []
                                
                                self.price_history[symbol].append({
                                    'price': current_price,
                                    'timestamp': int(time.time()),
                                    'volume': float(coin_data.get('usd_24h_vol', 0))
                                })
                                
                                # Keep only last 200 prices
                                if len(self.price_history[symbol]) > 200:
                                    self.price_history[symbol] = self.price_history[symbol][-200:]
                                
                                return {
                                    'symbol': symbol,
                                    'price': current_price,
                                    'volume': float(coin_data.get('usd_24h_vol', 0)),
                                    'change_24h': float(coin_data.get('usd_24h_change', 0)),
                                    'timestamp': int(time.time()),
                                    'last_updated': coin_data.get('last_updated_at', int(time.time()))
                                }
                            else:
                                logger.warning(f"⚠️ No data for {symbol}")
                                return {}
                                
                        elif response.status == 429:
                            wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20 seconds
                            logger.warning(f"⚠️ Rate limit hit for {symbol} (attempt {attempt + 1}/{max_retries}) - waiting {wait_time}s")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            logger.error(f"❌ Error fetching {symbol}: {response.status}")
                            return {}
                            
                except Exception as e:
                    logger.error(f"❌ Error in attempt {attempt + 1} for {symbol}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(5)
                        continue
                    else:
                        return {}
            
            # If all retries failed
            logger.error(f"❌ All retry attempts failed for {symbol}")
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
            logger.info("🧹 CoinGeckoSimpleSource cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")