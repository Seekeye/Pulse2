"""
Coinbase Source - Compatible with existing ChainPulse structure
Uses Coinbase Exchange API (Production)
"""
import logging
import asyncio
import aiohttp
import hmac
import hashlib
import base64
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from .base_collector import BaseDataCollector

logger = logging.getLogger(__name__)

class CoinbaseSource(BaseDataCollector):
    """Coinbase data source using Exchange API (Production)"""
    
    def __init__(self, config_dict: Dict[str, Any]):
        super().__init__(config_dict)
        
        # API Configuration
        self.api_key = config_dict.get('api_key', '')
        self.api_secret = config_dict.get('api_secret', '')
        self.passphrase = config_dict.get('passphrase', '')
        self.sandbox = config_dict.get('sandbox', False)  # ← CAMBIADO: Default False
        
        # URLs - CORREGIDAS PARA PRODUCCIÓN
        if self.sandbox:
            # Sandbox URLs (solo para testing)
            self.base_url = "https://api-public.sandbox.exchange.coinbase.com"
            self.ws_url = "wss://ws-feed-public.sandbox.exchange.coinbase.com"
        else:
            # Production URLs - CORREGIDAS
            self.base_url = "https://api.exchange.coinbase.com"
            self.ws_url = "wss://ws-feed.exchange.coinbase.com"
        
        self.session = None
        logger.info(f"🔧 CoinbaseSource collector created (Production Mode)")

    async def initialize(self) -> bool:
        """Initialize Coinbase connection"""
        try:
            # Configurar headers para requests
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'ChainPulse/1.0',
                    'Accept': 'application/json'
                }
            )
            
            # Test connection using the test_connection method
            if await self.test_connection():
                self.is_initialized = True
                logger.info("✅ Coinbase connection successful")
                return True
            else:
                logger.error("❌ Coinbase connection failed")
                return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing Coinbase: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection to Coinbase"""
        try:
            # Usar endpoint público que no requiere autenticación
            test_url = f"{self.base_url}/products"
            
            async with self.session.get(test_url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Verificar que recibimos datos válidos
                    if isinstance(data, list) and len(data) > 0:
                        self.connection_status = True
                        logger.info(f"✅ Coinbase connection test successful - {len(data)} products available")
                        return True
                    else:
                        logger.error("❌ Invalid response format from Coinbase")
                        return False
                else:
                    self.connection_status = False
                    logger.error(f"❌ Coinbase connection test failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
            self.connection_status = False
            return False

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get current market data for a symbol"""
        try:
            # Get ticker data
            ticker_url = f"{self.base_url}/products/{symbol}/ticker"
            
            async with self.session.get(ticker_url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Validar que tenemos datos válidos
                    if 'price' in data and data['price']:
                        return {
                            'symbol': symbol,
                            'price': float(data.get('price', 0)),
                            'volume': float(data.get('volume', 0)),
                            'bid': float(data.get('bid', 0)),
                            'ask': float(data.get('ask', 0)),
                            'timestamp': int(time.time()),
                            'high_24h': float(data.get('high', 0)),
                            'low_24h': float(data.get('low', 0)),
                            'open_24h': float(data.get('open', 0))
                        }
                    else:
                        logger.warning(f"⚠️ Invalid price data for {symbol}")
                        return {}
                        
                elif response.status == 404:
                    logger.error(f"❌ Symbol {symbol} not found (404) - Check if symbol exists")
                    return {}
                else:
                    logger.error(f"❌ Error fetching {symbol}: {response.status}")
                    return {}
                    
        except Exception as e:
            logger.error(f"❌ Error getting data for {symbol}: {e}")
            return {}

    async def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[List]:
        """Get historical candle data"""
        try:
            # Convert timeframe to Coinbase format
            granularity_map = {
                '1m': 60,
                '5m': 300,
                '15m': 900,
                '1h': 3600,
                '6h': 21600,
                '1d': 86400
            }
            
            granularity = granularity_map.get(timeframe, 3600)
            
            # Calculate time range
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(seconds=granularity * limit)
            
            candles_url = f"{self.base_url}/products/{symbol}/candles"
            params = {
                'start': start_time.isoformat(),
                'end': end_time.isoformat(),
                'granularity': granularity
            }
            
            async with self.session.get(candles_url, params=params) as response:
                if response.status == 200:
                    candles = await response.json()
                    
                    # Validar que recibimos datos
                    if not candles or len(candles) == 0:
                        logger.warning(f"⚠️ No historical data available for {symbol}")
                        return None
                    
                    # Convert to standard format
                    formatted_candles = []
                    for candle in candles:
                        if len(candle) >= 6:  # Validar formato
                            formatted_candles.append({
                                'timestamp': candle[0],
                                'low': float(candle[1]),
                                'high': float(candle[2]),
                                'open': float(candle[3]),
                                'close': float(candle[4]),
                                'volume': float(candle[5])
                            })
                    
                    return sorted(formatted_candles, key=lambda x: x['timestamp'])
                    
                elif response.status == 404:
                    logger.error(f"❌ Historical data for {symbol} not found (404)")
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
            if hasattr(self, 'stop'):
                await self.stop()
            logger.info("🧹 CoinbaseSource cleaned up")
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")