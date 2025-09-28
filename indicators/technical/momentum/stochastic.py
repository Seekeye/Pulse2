""" Stochastic Oscillator Indicator """
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class StochasticIndicator:
    """ Stochastic Oscillator indicator """
    
    def __init__(self, k_period: int = 14, d_period: int = 3):
        self.k_period = k_period
        self.d_period = d_period
        self.category = "momentum"
        self.name = "Stochastic"
        
        logger.debug(f"StochasticIndicator created: k_period={k_period}, d_period={d_period}")

    async def calculate(self, data: List[Dict]) -> Dict[str, Any]:
        """ Calculate Stochastic Oscillator """
        try:
            if len(data) < self.k_period + self.d_period:
                return {"error": f"Insufficient data: need at least {self.k_period + self.d_period} points"}

            # Extract OHLC data
            highs = [float(candle['high']) for candle in data]
            lows = [float(candle['low']) for candle in data]
            closes = [float(candle['close']) for candle in data]
            
            # Calculate %K
            k_values = []
            for i in range(self.k_period - 1, len(data)):
                period_highs = highs[i - self.k_period + 1:i + 1]
                period_lows = lows[i - self.k_period + 1:i + 1]
                current_close = closes[i]
                
                highest_high = max(period_highs)
                lowest_low = min(period_lows)
                
                if highest_high != lowest_low:
                    k_value = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
                else:
                    k_value = 50  # Neutral when no range
                    
                k_values.append(k_value)
            
            # Calculate %D (SMA of %K)
            d_values = []
            for i in range(self.d_period - 1, len(k_values)):
                period_k = k_values[i - self.d_period + 1:i + 1]
                d_value = sum(period_k) / len(period_k)
                d_values.append(d_value)
            
            # Get current values
            current_k = k_values[-1]
            current_d = d_values[-1]
            previous_k = k_values[-2] if len(k_values) > 1 else current_k
            previous_d = d_values[-2] if len(d_values) > 1 else current_d
            
            # Determine signal strength
            signal_strength = self._calculate_signal_strength(current_k, current_d, previous_k, previous_d)
            
            # Determine signal direction
            signal_direction = self._determine_signal_direction(current_k, current_d, previous_k, previous_d)
            
            # Determine overbought/oversold
            market_condition = self._determine_market_condition(current_k, current_d)
            
            return {
                "indicator_name": "Stochastic",
                "category": self.category,
                "k_percent": current_k,
                "d_percent": current_d,
                "signal_strength": signal_strength,
                "signal_direction": signal_direction,
                "market_condition": market_condition,
                "crossover": self._detect_crossover(k_values, d_values),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic: {e}")
            return {"error": str(e)}

    def _calculate_signal_strength(self, k: float, d: float, prev_k: float, prev_d: float) -> float:
        """ Calculate signal strength """
        try:
            # Base strength from position in range
            position_strength = 0
            if k > 80 or k < 20:  # Extreme levels
                position_strength = 80
            elif k > 70 or k < 30:  # Strong levels
                position_strength = 60
            elif k > 60 or k < 40:  # Moderate levels
                position_strength = 40
            else:  # Neutral zone
                position_strength = 20
                
            # Crossover bonus
            crossover_bonus = 0
            if (k > d and prev_k <= prev_d) or (k < d and prev_k >= prev_d):
                crossover_bonus = 20
                
            # Divergence bonus
            divergence_bonus = 0
            if abs(k - d) > abs(prev_k - prev_d):
                divergence_bonus = 10
                
            total_strength = min(position_strength + crossover_bonus + divergence_bonus, 100)
            return max(0, total_strength)
            
        except Exception as e:
            logger.error(f"Error calculating Stochastic signal strength: {e}")
            return 50.0

    def _determine_signal_direction(self, k: float, d: float, prev_k: float, prev_d: float) -> str:
        """ Determine signal direction """
        if k > d and k < 20:  # Oversold and %K above %D
            return "BUY"
        elif k < d and k > 80:  # Overbought and %K below %D
            return "SELL"
        elif k > d:  # %K above %D
            return "BUY"
        elif k < d:  # %K below %D
            return "SELL"
        else:
            return "NEUTRAL"

    def _determine_market_condition(self, k: float, d: float) -> str:
        """ Determine market condition """
        if k > 80 and d > 80:
            return "OVERBOUGHT"
        elif k < 20 and d < 20:
            return "OVERSOLD"
        elif k > 50 and d > 50:
            return "BULLISH"
        elif k < 50 and d < 50:
            return "BEARISH"
        else:
            return "NEUTRAL"

    def _detect_crossover(self, k_values: List[float], d_values: List[float]) -> str:
        """ Detect recent crossovers """
        if len(k_values) < 2 or len(d_values) < 2:
            return "NONE"
            
        current_k = k_values[-1]
        current_d = d_values[-1]
        prev_k = k_values[-2]
        prev_d = d_values[-2]
        
        if prev_k <= prev_d and current_k > current_d:
            return "BULLISH_CROSSOVER"
        elif prev_k >= prev_d and current_k < current_d:
            return "BEARISH_CROSSOVER"
        else:
            return "NONE"
