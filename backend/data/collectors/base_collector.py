""" Base Data Collectors - Abstract base class for all data collectors """
import logging 
from abc import ABC, abstractmethod 
from typing import Dict, List, Optional, Any 
from datetime import datetime 

logger = logging.getLogger(__name__)

class BaseDataCollector(ABC):
    """ Abstract base class for data collectors """

    def __init__(self, settings):
        self.settings = settings 
        self.name = self.__class__.__name__
        self.is_initialized = False 
        self.connection_status = False 

        logger.info(f"🔧 {self.name} collector created")
    
    @abstractmethod
    async def initialize(self) -> bool:
        """ Initialize the data collector """
        pass 

    @abstractmethod 
    async def test_connection(self) -> bool:
        """ Test connection to data source """
        pass 

    @abstractmethod 
    async def get_historical_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[List]:
        """ Get historical data for a symbol """
        pass 

    async def get_multiple_symbols(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """ Get data for multiple symbols """
        logger.debug(f"📊 Fetching data for {len(symbols)} symbols...")

        results = {}
        for symbol in symbols:
            try:
                data = await self.get_symbol_data(symbol)
                if data:
                    results[symbol] = data

                    logger.debug(f"✅ Data fetched for {symbol}")
                else:
                    logger.warning(f"⚠️ No data for {symbol}")
            except Exception as e:
                logger.error(f"❌ Error fetching {symbol}: {e}")
                continue 

        logger.info(f"📊 Successfully fetched data for {len(results)}/{len(symbols)} symbols")
        return results 

    async def stop(self):
        """ Stop the data collector """
        logger.info(f"🛑 Stopping {self.name} collector...")
        self.connection_status = False
        self.is_initialized = False 