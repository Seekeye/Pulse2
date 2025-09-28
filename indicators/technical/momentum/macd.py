""" MACD Indicator - Moving Average Convergence Divergence """
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MACDIndicator:
    """ MACD (Moving Average Convergence Divergence) indicator """
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.category = "momentum"
        self.name = "MACD"
        
        logger.debug(f"MACDIndicator created: fast={fast_period}, slow={slow_period}, signal={signal_period}")

    async def calculate(self, data: List[Dict]) -> Dict[str, Any]:
        """ Calculate MACD indicator """
        try:
            if len(data) < self.slow_period + self.signal_period:
                return {"error": f"Insufficient data: need at least {self.slow_period + self.signal_period} points"}

            # Extract closing prices
            closes = [float(candle['close']) for candle in data]
            
            # Calculate EMAs
            fast_ema = self._calculate_ema(closes, self.fast_period)
            slow_ema = self._calculate_ema(closes, self.slow_period)
            
            # Calculate MACD line
            macd_line = [fast - slow for fast, slow in zip(fast_ema, slow_ema)]
            
            # Calculate signal line (EMA of MACD)
            signal_line = self._calculate_ema(macd_line, self.signal_period)
            
            # Calculate histogram
            histogram = [macd - signal for macd, signal in zip(macd_line, signal_line)]
            
            # Get current values
            current_macd = macd_line[-1]
            current_signal = signal_line[-1]
            current_histogram = histogram[-1]
            previous_macd = macd_line[-2] if len(macd_line) > 1 else current_macd
            previous_signal = signal_line[-2] if len(signal_line) > 1 else current_signal
            
            # Determine signal strength
            signal_strength = self._calculate_signal_strength(
                current_macd, current_signal, current_histogram,
                previous_macd, previous_signal
            )
            
            # Determine signal direction
            signal_direction = self._determine_signal_direction(
                current_macd, current_signal, current_histogram
            )
            
            return {
                "indicator_name": "MACD",
                "category": self.category,
                "macd_line": current_macd,
                "signal_line": current_signal,
                "histogram": current_histogram,
                "signal_strength": signal_strength,
                "signal_direction": signal_direction,
                "trend": "bullish" if current_macd > current_signal else "bearish",
                "crossover": self._detect_crossover(macd_line, signal_line),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return {"error": str(e)}

    def _calculate_ema(self, data: List[float], period: int) -> List[float]:
        """ Calculate Exponential Moving Average """
        if not data:
            return []
            
        ema = [data[0]]  # First value is the same as the first data point
        multiplier = 2 / (period + 1)
        
        for i in range(1, len(data)):
            ema_value = (data[i] * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
            
        return ema

    def _calculate_signal_strength(self, macd: float, signal: float, histogram: float, 
                                 prev_macd: float, prev_signal: float) -> float:
        """ Calculate signal strength based on MACD values """
        try:
            # Base strength from histogram magnitude
            histogram_strength = min(abs(histogram) * 100, 100)
            
            # Crossover bonus
            crossover_bonus = 0
            if (macd > signal and prev_macd <= prev_signal) or (macd < signal and prev_macd >= prev_signal):
                crossover_bonus = 20
                
            # Divergence bonus
            divergence_bonus = 0
            if abs(macd - signal) > abs(prev_macd - prev_signal):
                divergence_bonus = 10
                
            total_strength = min(histogram_strength + crossover_bonus + divergence_bonus, 100)
            return max(0, total_strength)
            
        except Exception as e:
            logger.error(f"Error calculating MACD signal strength: {e}")
            return 50.0

    def _determine_signal_direction(self, macd: float, signal: float, histogram: float) -> str:
        """ Determine signal direction """
        if macd > signal and histogram > 0:
            return "BUY"
        elif macd < signal and histogram < 0:
            return "SELL"
        else:
            return "NEUTRAL"

    def _detect_crossover(self, macd_line: List[float], signal_line: List[float]) -> str:
        """ Detect recent crossovers """
        if len(macd_line) < 2 or len(signal_line) < 2:
            return "NONE"
            
        current_macd = macd_line[-1]
        current_signal = signal_line[-1]
        prev_macd = macd_line[-2]
        prev_signal = signal_line[-2]
        
        if prev_macd <= prev_signal and current_macd > current_signal:
            return "BULLISH_CROSSOVER"
        elif prev_macd >= prev_signal and current_macd < current_signal:
            return "BEARISH_CROSSOVER"
        else:
            return "NONE"
