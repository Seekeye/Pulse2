""" Exponential Moving Average (EMA) Indicator """
import logging 
import numpy as np 
from typing import Dict, List, Any
from ...base_indicators import BaseIndicator 

logger = logging.getLogger(__name__)

class EMAIndicator(BaseIndicator):
    def __init__(self, period: int = 12):
        super().__init__("EMA", "trend", period)
        self.multiplier = 2.0 / (period + 1)
        logger.info(f"EMA indicator initialized (period={period})")

    async def calculate(self, data: List[Dict], **kwargs) -> Dict[str, Any]:
        """ Calculate Exponential Moving Average """
        try:
            if not self.validate_data(data, self.period):
                return {"error": "Invalid data"}

            # Extract close prices 
            closes = self.extract_prices(data, 'close')
            if len(closes) == 0:
                return {"error": "No price data"}

            # Calculate EMA
            ema_values = []

            # Start with SMA for first value 
            first_ema = np.mean(closes[:self.period])
            ema_values.append(first_ema)

            # Calculate subsequent EMA values 
            for i in range(self.period, len(closes)):
                ema = (closes[i] * self.multiplier) + (ema_values[-1] * (1 - self.multiplier))
                ema_values.append(ema)

            current_ema = ema_values[-1]
            current_price = closes[-1]

            # Calculate price position relative to EMA
            price_vs_ema = ((current_price - current_ema) / current_ema) * 100

            # Calculate EMA slope (trend strength)
            ema_slope = 0.0
            if len(ema_values) >= 2:
                ema_slope = ((current_ema - ema_values[-2]) / ema_values[-2]) * 100
 
            # Determine signal strength 
            trend_strength = self.get_signal_strength(current_ema, ema_values[:-1])

            result = {
                "value": current_ema,
                "current_price": current_price,
                "price_vs_ema": price_vs_ema,
                "ema_slope": ema_slope,
                "signal": "BULLISH" if current_price > current_ema else "BEARISH",
                "historical_values": ema_values[-10:], # Last 10 values
                "timestamp": data[-1]['timestamp']
            }

            logger.debug(f"EMA calculated: {current_ema:.4f} (slope: {ema_slope:+.3f}%)")
            return result 

        except Exception as e:
            logger.error(f"EMA calculation error: {e}")
            return {"error": str(e)}

    def get_signal_strength(self, current_value: float, historical_values: List[float]) -> float:
        """ Calculate signal strength based on EMA slope and momentum """
        try:
            if len(historical_values) < 3:
                return 50.0

            # Calculate recent slopes 
            recent_values = historical_values[-3:] + [current_value]
            slopes = []

            for i in range(1, len(recent_values)):
                slope = (recent_values[i] - recent_values[i -1]) / recent_values[i-1] * 100
                slopes.append(slope)

            # Current slope magnitude 
            current_slope = slopes[-1] if slopes else 0
            slope_magnitude = abs(current_slope)

            # Slope acceleration (is trend accelerating?)
            acceleration = 0
            if len(slopes) >= 2:
                acceleration = slopes[-1] - slopes[-2]

            # Base strength from slope magnitude 
            base_strength = min(slope_magnitude * 25, 80)

            # Bonus dor acceleration in same direction 
            if (current_slope > 0 and acceleration > 0) or (current_slope < 0 and acceleration < 0):
                base_strength += 20

            return min(base_strength, 100.0)

        except Exception as e:
            logger.error(f"EMA signal strength error: {e}")
            return 50.0
