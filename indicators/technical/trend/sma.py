""" Simple Moving Average (SMA) Indicator """

import logging 
import numpy as np 
from typing import Dict, List, Any 
from ...base_indicators import BaseIndicator 

logger = logging.getLogger(__name__)

class SMAIndicator(BaseIndicator):
    """ Simple Moving Average indicator """

    def __init__(self, period: int = 20):
        super().__init__("SMA", "trend", period)
        logger.info(f"SMA Indicator initialized (period={period})")
 
    async def calculate(self, data: List[Dict], **kwargs) -> Dict[str, Any]:
        """ Calculate Simple Moving Average """
        try:
            if not self.validate_data(data, self.period):
                return {"error": "Invalid data"}

            # Extract close prices 
            closes = self.extract_prices(data, 'close')
            if len(closes) == 0:
                return {"error": "No price data"}

            # Calculate SMA 
            sma_values = []
            for i in range(self.period - 1, len(closes)):
                sma = np.mean(closes[i - self.period + 1:i + 1])
                sma_values.append(float(sma))

            current_sma = sma_values[-1] if sma_values else 0.0
            current_price = float(data[-1]['close'])

            # Calculate price position relative to SMA
            price_vs_sma = ((current_price - current_sma) / current_sma) * 100

            # Determine trend strength 
            trend_strength = self.get_signal_strength(current_sma, sma_values[:-1])

            result = {
                "value": current_sma,
                "current_price": current_price,
                "price_vs_sma": price_vs_sma,
                "trend_strength": trend_strength,
                "signal": "BULLISH" if current_price > current_sma else "BEARISH",
                "historical_values": sma_values[-10:], # Last 10 values 
                "timestamp": data[-1]['timestamp']
            }

            logger.debug(f"SMA calculated: {current_sma:.4f} (price: {current_price:.4f}, {price_vs_sma:+.2f}%)")
            return result 

        except Exception as e:
            logger.error(f"SMA calculation error: {e}")
            return {"error": str(e)}

    def get_signal_strength(self, current_value: float, historical_values: List[float]) -> float:
        """ Calculate signal strength based on SMA slope and cosnistency """
        try:
            if len(historical_values) < 3:
                return 50.0 

            # Calculate slope of recent SMA values 
            recent_values = historical_values[-5:] + [current_value]
            slopes = []

            for i in range(1, len(recent_values)):
                slope = (recent_values[i] - recent_values[i-1]) / recent_values[i-1] * 100
                slopes.append(slope)

            # Average slope 
            avg_slope = np.mean(slopes)

            # Consistency (how consistent is the trend)
            slope_std = np.std(slopes)
            consistency = max(0, 100 - (slope_std * 10))

            # Combine slope maginitude and consistency
            slope_strength = min(abs(avg_slope) * 20, 100)
            signal_strength = (slope_strength * 0.7) + (consistency * 0.3)

            return min(signal_strength, 100.0)

        except Exception as e:
            logger.error(f"SMA signal strength error: {e}")
            return 50.0
