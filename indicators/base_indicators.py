""" Base Indicators - Abstract base class for all technical indicators """

import logging 
import numpy as np 
import pandas as pd 
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union 
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseIndicator(ABC):
    """ Abstract base class for technical indicators """

    def __init__(self, name:str, category: str, period: int = 14):
        self.name = name 
        self.category = category # trend, momentum, volatilty, volume 
        self.period = period
        self.is_initialized = False
        self.last_calculation = None 

        logger.debug(f"{self.name} indicator created (period={period})")

    @abstractmethod 
    async def calculate(self, data: List[Dict], **kwargs) -> Dict[str, Any]:
        """ Calculate the indicator value """
        pass 

    @abstractmethod
    def get_signal_strength(self, current_value: float, historical_values: List[float]) -> float:
        """ Get signal strength (0-100) based on indicator value """
        pass 

    def validate_data(self, data: List[Dict], min_periods: Optional[int] = None) -> bool:
        """ Validate input data """
        if not data:
            logger.warning(f"{self.name}: No data provided")
            return False 

        required_periods = min_periods or self.period
        if len(data) < required_periods:
            logger.warning(f"{self.name}: Insufficient data ({len(data)} < {required_periods})")
            return False 

        # Check for required fields
        required_fields = ['close', 'timestamp']
        for candle in data[-5:]: # Check last 5 candles 
            for field in required_fields:
                if field not in candle:
                    logger.error(f"{self.name}: Missing field '{field}' in data")
                    return False 

        return True 

    def extract_prices(self, data: List[Dict], price_type: str = 'close') -> np.ndarray:
        """ Extract price array from candle data """
        try:
            prices = [float(candle[price_type]) for candle in data]
            return np.array(prices)
        except (KeyError, ValueError) as e:
            logger.error(f"{self.name}: Error extracting {price_type} prices: {e}")
            return np.array([])

    def get_trend_direction(self, values: List[float], lookback: int = 3) -> str:
        """ Determine trend direction from recent values """
        if len(values) < lookback:
            return "NEUTRAL"
        
        recent_values = values[-lookback]
        if all(recent_values[i] > recent_values[i-1] for i in range(1, len(recent_values))):
            return "BULLISH"
        elif all(recent_values[i] < recent_values[i-1] for i in range(1, len(recent_values))):
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def normalize_signal(self, value: float, min_val: float, max_val: float) -> float:
        """ Normalize value to 0-100 range """
        if max_val == min_val:
            return 50.0
        
        normalized = ((value - min_val) / (max_val - min_val)) * 100
        return max(0.0, min(100.0, normalized))

    async def get_market_bias(self, current_value:float, historical_values: List[float]) -> Dict[str, Any]:
        """ Get market bias from indicator"""
        try:
            signal_strength = self.get_signal_strength(current_value, historical_values)
            trend_direction = self.get_trend_direction(historical_values + [current_value])

            # Determine bias 
            if signal_strength > 70:
                bias = "STRONG_" + ("BULLISH" if trend_direction == "BULLISH" else "BEARISH")
            elif signal_strength > 50:
                bias = "WEAK_" + ("BULLISH" if trend_direction == "BULLISH" else "BEARISH")
            else:
                bias = "NEUTRAL"

            return {
                "bias": bias,
                "strength": signal_strength,
                "direction": trend_direction,
                "confidence": min(signal_strength, 100.0)
            }

        except Exception as e: 
            logger.error(f"{self.name}: Error calculatig market bias: {e}")
            return {
                "bias": "NEUTRAL",
                "strength": 0.0, 
                "direction": "NEUTRAL",
                "confidence": 0.0
            }