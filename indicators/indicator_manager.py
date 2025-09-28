""" Indicator Manager - Manage all technical indicators """
import logging 
import asyncio
from typing import Dict, List, Any, Optional 
from datetime import datetime 

from .technical.trend.sma import SMAIndicator 
from .technical.trend.ema import EMAIndicator 
from .technical.trend.bollinger_bands import BollingerBandsIndicator
from .technical.momentum.rsi import RSIIndicator
from .technical.momentum.macd import MACDIndicator
from .technical.momentum.stochastic import StochasticIndicator 

logger = logging.getLogger(__name__)
 
class IndicatorManager:
    """ Manages all technical indicators """

    def __init__(self):
        self.indicators = {}
        self.indicator_weights = {}
        self.is_initialized = False 

        logger.info("IndicatorManager created")

    async def initialize(self) -> bool:
        """ Initialzie all indicators """
        try:
            logger.info("Initializing technical indicators...")

            # Initialize trend indicators 
            self.indicators["SMA_20"] = SMAIndicator(period=20)
            self.indicators["SMA_50"] = SMAIndicator(period=50)
            self.indicators["EMA_12"] = EMAIndicator(period=12)
            self.indicators["EMA_26"] = EMAIndicator(period=26)
            self.indicators["BB_20"] = BollingerBandsIndicator(period=20, std_dev=2.0)

            # Initialize momentum indicators
            self.indicators["RSI_14"] = RSIIndicator(period=14)
            self.indicators["MACD_12_26_9"] = MACDIndicator(fast_period=12, slow_period=26, signal_period=9)
            self.indicators["STOCH_14_3"] = StochasticIndicator(k_period=14, d_period=3)

            # Set default weights - REDISTRIBUIDOS PARA NUEVOS INDICADORES
            self.indicator_weights = {
                "SMA_20": 0.10,
                "SMA_50": 0.15,
                "EMA_12": 0.15,
                "EMA_26": 0.15,
                "BB_20": 0.15,
                "RSI_14": 0.10,
                "MACD_12_26_9": 0.10,
                "STOCH_14_3": 0.10
            }

            self.is_initialized = True
            logger.info(f"{len(self.indicators)} indicators initialized")

            # Log indicators details 
            for name, indicator in self.indicators.items():
                weight = self.indicator_weights.get(name, 0) * 100
                logger.info(f"{name}: {indicator.category} (weight: {weight:.1f}%)")
            
            return True 
        
        except Exception as e:
            logger.error(f"Error initializing indicators: {e}")
            return False 

    async def calculate_indicators(self, symbol: str, data: List[Dict], market_context: Dict) -> Dict[str, Any]:
        """ Calculate all indicators for a symbol """
        try:
            if not self.is_initialized:
                logger.warning("IndicatorManager not initialized")
                return {}

            logger.debug(f"Calculating indicators for {symbol}...")

            results = {}
            calculation_tasks = []

            # Create calculation tasks or all indicators
            for name, indicator in self.indicators.items():
                task = self._calculate_single_indicator(name, indicator, data)
                calculation_tasks.append(task)

            # Execute all calculations concurrently 
            calculation_results = await asyncio.gather(*calculation_tasks, return_exceptions=True)

            # Process results
            successful_calculations = 0
            for i, (name, result) in enumerate(zip(self.indicators.keys(), calculation_results)):
                if isinstance(result, Exception):
                    logger.error(f"Error calculating {name}: {result}")
                    continue 

                if result and "error" not in result:
                    results[name] = result 
                    successful_calculations += 1
                    logger.debug(f"{name} calculated successfully")
                else:
                    logger.warning(f"{name} calculation returned error: {result.get('error', 'Unknown')}")
            
            logger.info(f"{successful_calculations}/{len(self.indicators)} indicators calculated for {symbol}")

            # Calculate composite scores 
            composite_scores = await self._calculate_composite_scores(results, market_context)
            results["composite"] = composite_scores 

            return results 
        
        except Exception as e:
            logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}

    async def _calculate_single_indicator(self, name: str, indicator, data: List[Dict]) -> Dict[str, Any]:
        """ Calculate a single indicator """
        try:
            result = await indicator.calculate(data)
            if result and "error" not in result:
                result["indicator_name"] = name
                result["category"] = indicator.category 
                result["weight"] = self.indicator_weights.get(name, 0)
            return result 
        except Exception as e:
            logger.error(f"Error in {name} calculation: {e}")
            return {"error": str(e)}

    async def _calculate_composite_scores(self, indicator_results: Dict, market_context: Dict) -> Dict[str, Any]:
        """ Calculate composite scores from all indicators """
        try:
            trend_score = 0.0
            momentum_score = 0.0
            total_weight = 0.0

            contributing_indicators = []
            indicator_scores = {}

            for name, result in indicator_results.items():
                if "error" in result or "signal_strength" not in result:
                    continue 
                    
                weight = self.indicator_weights.get(name, 0)
                strength = result.get("signal_strength", 0)
                category = result.get("category", "unknown")

                # Weight the strength 
                weighted_strength = strength * weight 
                total_weight += weight 

                # Categorize scores 
                if category == "trend":
                    trend_score += weighted_strength
                elif category == "momentum":
                    momentum_score += weighted_strength

                # Track contributing indicators - MENOS EXIGENTE
                if strength > 45: # REDUCIDO DE 60 A 45 - incluir señales moderadas
                    contributing_indicators.append(name)
                    indicator_scores[name] = strength 
                
            # Normalize scores 
            if total_weight > 0:
                overall_score = (trend_score + momentum_score) / total_weight 
            else:
                overal_score = 50.0

            # Determine overall bias 
            overall_bias = "NEUTRAL"
            if overall_score > 70:
                overall_bias = "STRONG_BULLISH"
            elif overall_score > 55:
                overall_bias = "BULLISH"
            elif overall_score < 30:
                overall_bias = "STRONG_BEARISH"
            elif overall_score < 45:
                overall_bias = "BEARISH"

            composite = {
                "overall_score": overall_score,
                "trend_score": trend_score / max(total_weight * 0.6, 0.1), # Assuming 60% trend weight 
                "momentum_score": momentum_score / max(total_weight * 0.4, 0.1), # Assuming 40% momentum weight 
                "overall_bias": overall_bias,
                "contributing_indicators": contributing_indicators,
                "indicator_scores": indicator_scores,
                "total_indicators": len(indicator_results),
                "successful_indicators": len([r for r in indicator_results.values() if "error" not in r])
            }

            logger.debug(f"Composite score: Overall={overall_score:.1f} ({overall_bias})")
            return composite 

        except Exception as e:
            logger.error(f"Error calculating composite scores: {e}")
            return {
                "overall_score": 50.0,
                "trend_score": 50.0,
                "momentum_score": 50.0,
                "overall_bias": "NEUTRAL",
                "contributing_indicators": [],
                "indicators_scores": {},
                "error": str(e)
            }

    def get_indicator_count(self) -> int:
        """ Get total number of indicators """
        return len(self.indicators)

    def get_indicator_names(self) -> List[str]:
        """ Get list of indicator names """
        return list(self.indicators.keys())

    def update_weights(self, new_weights: Dict[str, float]):
        """ Update indicator weights """
        try:
            for name, weight in new_weights.items():
                if name in self.indicator_weights:
                    self.indicator_weights[name] = weight
                    logger.info(f"Updated {name} weight to {weigth:.3f}")

            # Normalize weights to sum 1.0
            total_weight = sum(self.indicator_weights.values())
            if total_weight > 0:
                for name in self.indicator_weights:
                    self.indicator_weights[name] /= total_weight 

            logger.info("Indicator weights updated and normalized")

        except Exception as e:
            logger.error(f"Error updating weights: {e}")
