"""
Multi-Source Collector - Intelligent fallback system
Tries multiple data sources in order of preference
"""
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .base_collector import BaseDataCollector
from .binance_collector import BinanceSource
from .coincap_collector import CoinCapSource
from .cryptocompare_collector import CryptoCompareSource
from .coingecko_simple import CoinGeckoSimpleSource

logger = logging.getLogger(__name__)

class MultiSourceCollector(BaseDataCollector):
    """Multi-source data collector with intelligent fallback"""
    
    def __init__(self, settings):
        super().__init__(settings)
        
        self.settings = settings
        self.sources = []
        self.current_source_index = 0
        self.source_stats = {}
        self.last_successful_source = None
        
        # Initialize all available sources
        self._initialize_sources()
        
        logger.info(f"🔧 MultiSourceCollector created with {len(self.sources)} sources")

    def _initialize_sources(self):
        """Initialize all available data sources"""
        try:
            # Order by preference (best to worst)
            source_configs = [
                ("binance", BinanceSource, self.settings.get_binance_config()),
                ("coincap", CoinCapSource, self.settings.get_coincap_config()),
                ("cryptocompare", CryptoCompareSource, self.settings.get_cryptocompare_config()),
                ("coingecko", CoinGeckoSimpleSource, self.settings.get_coingecko_config())
            ]
            
            for source_name, source_class, config in source_configs:
                try:
                    source = source_class(config)
                    self.sources.append({
                        'name': source_name,
                        'instance': source,
                        'enabled': True,
                        'last_error': None,
                        'error_count': 0,
                        'success_count': 0
                    })
                    self.source_stats[source_name] = {
                        'total_requests': 0,
                        'successful_requests': 0,
                        'failed_requests': 0,
                        'last_success': None,
                        'last_error': None
                    }
                    logger.info(f"✅ {source_name.title()} source initialized")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize {source_name}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error initializing sources: {e}")

    async def initialize(self) -> bool:
        """Initialize the multi-source collector"""
        try:
            logger.info("🔄 Initializing multi-source collector...")
            
            # Try to initialize sources in order
            for i, source_info in enumerate(self.sources):
                if not source_info['enabled']:
                    continue
                    
                try:
                    source = source_info['instance']
                    if await source.initialize():
                        self.current_source_index = i
                        self.last_successful_source = source_info['name']
                        logger.info(f"✅ Primary source set to: {source_info['name']}")
                        self.is_initialized = True
                        return True
                    else:
                        logger.warning(f"⚠️ {source_info['name']} initialization failed")
                        source_info['enabled'] = False
                        
                except Exception as e:
                    logger.warning(f"⚠️ {source_info['name']} initialization error: {e}")
                    source_info['enabled'] = False
                    continue
            
            # If no source initialized successfully
            logger.error("❌ No data sources could be initialized")
            return False
                    
        except Exception as e:
            logger.error(f"❌ Error initializing multi-source collector: {e}")
            return False

    async def test_connection(self) -> bool:
        """Test connection using current source"""
        try:
            if not self.sources or self.current_source_index >= len(self.sources):
                return False
                
            current_source = self.sources[self.current_source_index]
            if not current_source['enabled']:
                return await self._try_next_source()
                
            source = current_source['instance']
            if await source.test_connection():
                return True
            else:
                return await self._try_next_source()
                
        except Exception as e:
            logger.error(f"❌ Connection test error: {e}")
            return await self._try_next_source()

    async def get_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """Get symbol data with automatic fallback"""
        try:
            # Try current source first
            if await self._try_current_source():
                data = await self.sources[self.current_source_index]['instance'].get_symbol_data(symbol)
                if data:
                    await self._record_success(self.current_source_index)
                    return data
            
            # Try other sources
            for i, source_info in enumerate(self.sources):
                if not source_info['enabled'] or i == self.current_source_index:
                    continue
                    
                try:
                    data = await source_info['instance'].get_symbol_data(symbol)
                    if data:
                        # Switch to this source
                        self.current_source_index = i
                        self.last_successful_source = source_info['name']
                        await self._record_success(i)
                        logger.info(f"🔄 Switched to {source_info['name']} for {symbol}")
                        return data
                        
                except Exception as e:
                    await self._record_error(i, str(e))
                    continue
            
            logger.error(f"❌ All sources failed for {symbol}")
            return {}
            
        except Exception as e:
            logger.error(f"❌ Error getting data for {symbol}: {e}")
            return {}

    async def get_historical_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> Optional[List]:
        """Get historical data with automatic fallback"""
        try:
            # Try current source first
            if await self._try_current_source():
                data = await self.sources[self.current_source_index]['instance'].get_historical_data(symbol, timeframe, limit)
                if data:
                    return data
            
            # Try other sources
            for i, source_info in enumerate(self.sources):
                if not source_info['enabled'] or i == self.current_source_index:
                    continue
                    
                try:
                    data = await source_info['instance'].get_historical_data(symbol, timeframe, limit)
                    if data:
                        return data
                        
                except Exception as e:
                    await self._record_error(i, str(e))
                    continue
            
            logger.warning(f"⚠️ No historical data available for {symbol}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting historical data for {symbol}: {e}")
            return None

    async def _try_current_source(self) -> bool:
        """Try to use current source"""
        try:
            if not self.sources or self.current_source_index >= len(self.sources):
                return False
                
            current_source = self.sources[self.current_source_index]
            if not current_source['enabled']:
                return False
                
            source = current_source['instance']
            return source.is_initialized and source.connection_status
            
        except Exception as e:
            logger.error(f"❌ Error checking current source: {e}")
            return False

    async def _try_next_source(self) -> bool:
        """Try next available source"""
        try:
            for i, source_info in enumerate(self.sources):
                if not source_info['enabled']:
                    continue
                    
                source = source_info['instance']
                if await source.test_connection():
                    self.current_source_index = i
                    self.last_successful_source = source_info['name']
                    logger.info(f"🔄 Switched to {source_info['name']}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"❌ Error trying next source: {e}")
            return False

    async def _record_success(self, source_index: int):
        """Record successful request"""
        try:
            if source_index < len(self.sources):
                source_info = self.sources[source_index]
                source_name = source_info['name']
                
                source_info['success_count'] += 1
                self.source_stats[source_name]['successful_requests'] += 1
                self.source_stats[source_name]['last_success'] = datetime.utcnow()
                
        except Exception as e:
            logger.error(f"❌ Error recording success: {e}")

    async def _record_error(self, source_index: int, error_msg: str):
        """Record failed request"""
        try:
            if source_index < len(self.sources):
                source_info = self.sources[source_index]
                source_name = source_info['name']
                
                source_info['error_count'] += 1
                source_info['last_error'] = error_msg
                self.source_stats[source_name]['failed_requests'] += 1
                self.source_stats[source_name]['last_error'] = error_msg
                
                # Disable source if too many errors
                if source_info['error_count'] > 10:
                    source_info['enabled'] = False
                    logger.warning(f"⚠️ Disabled {source_name} due to too many errors")
                
        except Exception as e:
            logger.error(f"❌ Error recording error: {e}")

    async def get_source_status(self) -> Dict[str, Any]:
        """Get status of all sources"""
        try:
            status = {
                'current_source': self.sources[self.current_source_index]['name'] if self.sources else None,
                'last_successful_source': self.last_successful_source,
                'sources': {}
            }
            
            for source_info in self.sources:
                source_name = source_info['name']
                status['sources'][source_name] = {
                    'enabled': source_info['enabled'],
                    'success_count': source_info['success_count'],
                    'error_count': source_info['error_count'],
                    'last_error': source_info['last_error'],
                    'stats': self.source_stats.get(source_name, {})
                }
            
            return status
            
        except Exception as e:
            logger.error(f"❌ Error getting source status: {e}")
            return {}

    async def cleanup(self):
        """Cleanup all sources"""
        try:
            for source_info in self.sources:
                try:
                    await source_info['instance'].cleanup()
                except Exception as e:
                    logger.error(f"❌ Error cleaning up {source_info['name']}: {e}")
            
            logger.info("🧹 MultiSourceCollector cleaned up")
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
