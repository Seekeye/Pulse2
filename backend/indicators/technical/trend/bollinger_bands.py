""" Bollinger Bands Indicator """
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class BollingerBandsIndicator:
    """ Bollinger Bands indicator """
    
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.category = "trend"
        self.name = "BollingerBands"
        
        logger.debug(f"BollingerBandsIndicator created: period={period}, std_dev={std_dev}")

    async def calculate(self, data: List[Dict]) -> Dict[str, Any]:
        """ Calculate Bollinger Bands """
        try:
            if len(data) < self.period:
                return {"error": f"Insufficient data: need at least {self.period} points"}

            # Extract closing prices
            closes = [float(candle['close']) for candle in data]
            
            # Calculate Bollinger Bands
            upper_band, middle_band, lower_band = self._calculate_bands(closes)
            
            # Get current values
            current_price = closes[-1]
            current_upper = upper_band[-1]
            current_middle = middle_band[-1]
            current_lower = lower_band[-1]
            previous_price = closes[-2] if len(closes) > 1 else current_price
            
            # Calculate position within bands
            band_position = self._calculate_band_position(current_price, current_upper, current_middle, current_lower)
            
            # Determine signal strength
            signal_strength = self._calculate_signal_strength(
                current_price, current_upper, current_middle, current_lower,
                previous_price, band_position
            )
            
            # Determine signal direction
            signal_direction = self._determine_signal_direction(
                current_price, current_upper, current_middle, current_lower,
                previous_price, band_position
            )
            
            # Determine volatility
            volatility = self._determine_volatility(upper_band, lower_band, middle_band)
            
            return {
                "indicator_name": "BollingerBands",
                "category": self.category,
                "upper_band": current_upper,
                "middle_band": current_middle,
                "lower_band": current_lower,
                "band_position": band_position,
                "signal_strength": signal_strength,
                "signal_direction": signal_direction,
                "volatility": volatility,
                "squeeze": self._detect_squeeze(upper_band, lower_band, middle_band),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return {"error": str(e)}

    def _calculate_bands(self, closes: List[float]) -> tuple:
        """ Calculate Bollinger Bands """
        upper_band = []
        middle_band = []
        lower_band = []
        
        for i in range(self.period - 1, len(closes)):
            period_closes = closes[i - self.period + 1:i + 1]
            
            # Calculate SMA (middle band)
            sma = sum(period_closes) / len(period_closes)
            middle_band.append(sma)
            
            # Calculate standard deviation
            variance = sum((x - sma) ** 2 for x in period_closes) / len(period_closes)
            std = variance ** 0.5
            
            # Calculate upper and lower bands
            upper = sma + (self.std_dev * std)
            lower = sma - (self.std_dev * std)
            
            upper_band.append(upper)
            lower_band.append(lower)
            
        return upper_band, middle_band, lower_band

    def _calculate_band_position(self, price: float, upper: float, middle: float, lower: float) -> float:
        """ Calculate position within bands (0-1) """
        if upper == lower:
            return 0.5
        return (price - lower) / (upper - lower)

    def _calculate_signal_strength(self, price: float, upper: float, middle: float, lower: float,
                                 prev_price: float, band_position: float) -> float:
        """ Calculate signal strength """
        try:
            # Base strength from band position
            position_strength = 0
            if band_position > 0.95:  # Near upper band
                position_strength = 80
            elif band_position < 0.05:  # Near lower band
                position_strength = 80
            elif band_position > 0.8:  # Upper half
                position_strength = 60
            elif band_position < 0.2:  # Lower half
                position_strength = 60
            else:  # Middle area
                position_strength = 30
                
            # Bounce bonus
            bounce_bonus = 0
            if (band_position > 0.9 and price < prev_price) or (band_position < 0.1 and price > prev_price):
                bounce_bonus = 20
                
            # Breakout bonus
            breakout_bonus = 0
            if (prev_price <= upper and price > upper) or (prev_price >= lower and price < lower):
                breakout_bonus = 30
                
            total_strength = min(position_strength + bounce_bonus + breakout_bonus, 100)
            return max(0, total_strength)
            
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands signal strength: {e}")
            return 50.0

    def _determine_signal_direction(self, price: float, upper: float, middle: float, lower: float,
                                  prev_price: float, band_position: float) -> str:
        """ Determine signal direction """
        # Bounce signals
        if band_position < 0.1 and price > prev_price:
            return "BUY"  # Bounce from lower band
        elif band_position > 0.9 and price < prev_price:
            return "SELL"  # Bounce from upper band
            
        # Breakout signals
        if prev_price <= upper and price > upper:
            return "BUY"  # Breakout above upper band
        elif prev_price >= lower and price < lower:
            return "SELL"  # Breakout below lower band
            
        # Trend signals
        if price > middle:
            return "BUY"
        elif price < middle:
            return "SELL"
        else:
            return "NEUTRAL"

    def _determine_volatility(self, upper_band: List[float], lower_band: List[float], middle_band: List[float]) -> str:
        """ Determine volatility level """
        if len(upper_band) < 2:
            return "UNKNOWN"
            
        # Calculate band width
        current_width = upper_band[-1] - lower_band[-1]
        avg_width = sum(upper - lower for upper, lower in zip(upper_band, lower_band)) / len(upper_band)
        
        if current_width > avg_width * 1.5:
            return "HIGH"
        elif current_width < avg_width * 0.5:
            return "LOW"
        else:
            return "MEDIUM"

    def _detect_squeeze(self, upper_band: List[float], lower_band: List[float], middle_band: List[float]) -> bool:
        """ Detect Bollinger Bands squeeze (low volatility) """
        if len(upper_band) < 5:
            return False
            
        # Check if bands are converging
        recent_widths = [upper - lower for upper, lower in zip(upper_band[-5:], lower_band[-5:])]
        return all(recent_widths[i] <= recent_widths[i+1] for i in range(len(recent_widths)-1))
