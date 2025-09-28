""" Relative Strength Index (RSI) Indicator """
import logging 
import numpy as np 
from typing import Dict, List, Any
from ...base_indicators import BaseIndicator 

logger = logging.getLogger(__name__)

class RSIIndicator(BaseIndicator):
    """ Relative Strength Index Indicator """

    def __init__(self, period: int = 14):
        super().__init__("RSI", "momentum", period)
        logger.info(f"RSI Indicator initialized (period={period})")

    async def calculate(self, data: List[Dict], **kwargs) -> Dict[str, Any]:
        """ Calculate RSI """
        try:
            if not self.validate_data(data, self.period + 1):
                return {"error", "Invalid data"}

            # Extract close prices 
            closes = self.extract_prices(data, 'close')
            if len(closes) < self.period + 1:
                return {"error": "Insufficient data for RSI"}

            # Calculate price changes 
            price_changes = np.diff(closes)

            # Separate gains and losses 
            gains = np.where(price_changes > 0, price_changes, 0)
            losses = np.where(price_changes < 0, -price_changes, 0)

            # Calculate initial averages 
            avg_gain = np.mean(gains[:self.period])
            avg_loss = np.mean(losses[:self.period])

            # Calculate RSI values 
            rsi_values = []

            for i in range(self.period, len(price_changes)):
                # Smoothed averages (Wilder's smoothing)
                avg_gain = ((avg_gain * (self.period - 1)) + gains[i]) / self.period
                avg_loss = ((avg_loss * (self.period - 1)) + losses[i]) / self.period

                # Calculate RSI
                if avg_loss == 0:
                    rsi = 100.0
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100.0 - (100.0 / (1.0 + rs))

                rsi_values.append(rsi)

            current_rsi = rsi_values[-1] if rsi_values else 50.0
            current_price = float(data[-1]['close'])

            # Determine RSI signals 
            signal = "NEUTRAL"
            if current_rsi > 70:
                signal = "OVERBOUGHT"
            elif current_rsi < 30:
                signal = "OVERSOLD"
            elif current_rsi > 50:
                signal = "BULLISH"
            else:
                signal = "BEARISH"

            # Calculate signal strength 
            signal_strength = self.get_signal_strength(current_rsi, rsi_values[:-1])

            # Detect divergences(simplified)
            divergence = self._detect_divergence(closes[-10:], rsi_values[-10:])

            result = {
                "value": current_rsi,
                "current_price": current_price,
                "signal": signal,
                "signal_strength": signal_strength,
                "overbought": current_rsi > 70,
                "oversold": current_rsi < 30,
                "divergence": divergence,
                "historical_values": rsi_values[-10:],
                "timestamp": data[-1]['timestamp']
            }

            logger.debug(f"RSI calculated: {current_rsi:.2f} ({signal})")
            return result 
        
        except Exception as e:
            logger.error(f"RSI calculation error: {e}")
            return {"error": str(e)}

    def get_signal_strength(self, current_value: float, historical_values: List[float]) -> float:
        """ Calculate RSI signal strength """
        try:
            # Extreme levels give higher strength
            if current_value > 80 or current_value < 20:
                return 90.0
            elif current_value > 70 or current_value < 30:
                return 75.0

            # Check for momentum (RSI trend)
            if len(historical_values) >= 3:
                recent_rsi = historical_values[-3:] + [current_value]
                rsi_trend = recent_rsi[-1] - recent_rsi[0]

                # Strong momentum gives higher strength 
                momentum_strength = min(abs(rsi_trend) * 2, 60)

                # Distance from 50 (neutral)
                distance_strength = abs(current_value - 50) * 1.2

                return min(momentum_strength + distance_strength, 100.0)

            # Default based on distance from neutral 
            return abs(current_value - 50) * 1.5

        except Exception as e:
            logger.error(f"RSI signal strength error: {e}")
            return 50.0

    def _detect_divergence(self, prices: List[float], rsi_values: List[float]) -> str:
        """ Detect basic RSI divergence """
        try:
            if len(prices) < 4 or len(rsi_values) < 4:
                return "NONE"

            # Check if price made new high/low but RSI didn't
            price_trend = prices[-1] - prices[0]
            rsi_trend = rsi_values[-1] - rsi_values[0]

            if price_trend > 0 and rsi_trend < 0:
                return "BEARISH_DIVERGENCE"
            elif price_trend < 0 and rsi_trend > 0:
                return "BULLISH_DIVERGENCE"

            return "NONE"
        
        except Exception as e:
            logger.error(f"RSI divergence detection error: {e}")
            return "NONE"