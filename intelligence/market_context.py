""" Market Context Analyzer - Intelligent market context analysis """
""" Analyzes overall market conditions, trends, and volatilty """

import logging 
import numpy as np 
from typing import Dict, List, Any, Optional 
from datetime import datetime, timedelta 
from statistics import mean, stdev 

logger = logging.getLogger(__name__)

class MarketContextAnalyzer:
    """ Analyzer market context for intelligent signal generation """

    def __init__(self):
        self.name = "MarketContextAnalyzer"
        self.is_initialized = False 
        self.market_history = {}
        self.volatility_cache = {}

        logger.info("MarketContextAnalyzer created")
    
    async def initialize(self) -> bool:
        """ Initialize the market context analyzer """
        try:
            logger.info("Initializing MarketContextAnalyzer...")
            self.is_initialized = True
            logger.info("✅ MarketContextAnalyzer initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing MarketContextAnalyzer: {e}")
            return False
    
    async def analyze_market_context(self, market_data: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """ Analyze overall market context from all symbols """
        try:
            logger.debug("Analyzing market context...")

            if not market_data:
                logger.warning("No market data provided for context analysis")
                return self._get_default_context()

            # Analyze individual symbols 
            symbol_analyses = {}
            for symbol, data in market_data.items():
                analysis = await self._analyze_symbol_context(symbol, data)
                symbol_analyses[symbol] = analysis 

            # Aggregate market context 
            overall_context = await self._aggregate_market_context(symbol_analyses)

            # Update history 
            self._update_market_history(overall_context)

            logger.info(f"Market context: {overall_context.get('overall_trend', 'Unknown')} trend, {overall_context.get('volatility', 'Unknown')} volatility")
            return overall_context

        except Exception as e:
            logger.error(f"Error analyzing market context: {e}")
            return self._get_default_context()
        
    async def _analyze_symbol_context(self, symbol: str, data: Dict) -> Dict[str, Any]:
        """ Analyze context for a single symbol """
        try:
            current_price = float(data.get('price', 0))
            price_change_24h = float(data.get('price_change_percent', 0))
            volume_24h = float(data.get('volume', 0))
            high_24h = float(data.get('high_24h', current_price))
            low_24h = float(data.get('low_24h', current_price))

            # Calculate volatility 
            volatility = self._calculate_volatility(high_24h, low_24h, current_price)

            # Determine trend 
            trend = self._determine_trend(price_change_24h)

            # Calculate momentum 
            momentum = self._calculate_momentum(price_change_24h, volume_24h)

            # Volume analysis 
            volume_profile = self._analyze_volume(volume_24h, data.get('quote_volume', 0))

            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'volatility': volatility,
                'volatility_level': self._categorize_volatility(volatility),
                'trend': trend,
                'momentum': momentum,
                'volume_profile': volume_profile,
                'support_resistance': self._calculate_support_resistance(high_24h, low_24h, current_price)
            }

            logger.debug(f"{symbol}: {trend} trend, {volatility:.2f}% volatility")
            return analysis 

        except Exception as e:
            logger.error(f"Error analyzing {symbol} context: {e}")
            return {
                'symbol': symbol,
                'volatility': 0.0,
                'volatility_level': 'MEDIUM',
                'trend': 'NEUTRAL',
                'momentum': 0.0,
                'volume_profile': 'NORMAL'
            }

    async def _aggregate_market_context(self, symbol_analyses: Dict[str, Dict]) -> Dict[str, Any]:
        """ Aggregate individual symbol analyses into overall market context """
        try:
            if not symbol_analyses:
                return self._get_default_context()

            total_symbols = len(symbol_analyses)
            
            # Aggregate trends
            trend_counts = {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0}
            volatilities = []
            momentums = []
            
            for analysis in symbol_analyses.values():
                trend = analysis.get('trend', 'NEUTRAL')
                if trend in trend_counts:
                    trend_counts[trend] += 1
                
                volatilities.append(analysis.get('volatility', 0.0))
                momentums.append(analysis.get('momentum', 0.0))

            # Determine overall trend
            max_trend = max(trend_counts, key=trend_counts.get)
            trend_strength = trend_counts[max_trend] / total_symbols

            # Calculate average volatility
            avg_volatility = mean(volatilities) if volatilities else 0.0
            
            # Calculate market momentum
            avg_momentum = mean(momentums) if momentums else 0.0

            overall_context = {
                'overall_trend': max_trend,
                'trend_strength': trend_strength,
                'market_volatility': avg_volatility,
                'volatility_level': self._categorize_volatility(avg_volatility),
                'market_momentum': avg_momentum,
                'analyzed_symbols': total_symbols,
                'symbol_breakdown': trend_counts,
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': min(0.9, trend_strength + 0.1)
            }

            return overall_context

        except Exception as e:
            logger.error(f"Error aggregating market context: {e}")
            return self._get_default_context()

    def _calculate_volatility(self, high: float, low: float, current: float) -> float:
        """ Calculate volatility percentage """
        try:
            if current <= 0:
                return 0.0
            
            price_range = high - low
            volatility = (price_range / current) * 100
            return round(volatility, 2)
        except:
            return 0.0

    def _determine_trend(self, price_change_24h: float) -> str:
        """ Determine trend based on price change """
        if price_change_24h > 2.0:
            return 'BULLISH'
        elif price_change_24h < -2.0:
            return 'BEARISH'
        else:
            return 'NEUTRAL'

    def _calculate_momentum(self, price_change: float, volume: float) -> float:
        """ Calculate momentum score """
        try:
            # Simple momentum calculation
            momentum = abs(price_change) * (volume / 1000000)  # Normalize volume
            return round(momentum, 2)
        except:
            return 0.0

    def _analyze_volume(self, volume: float, quote_volume: float) -> str:
        """ Analyze volume profile """
        try:
            if volume > 1000000:  # High volume threshold
                return 'HIGH'
            elif volume > 100000:  # Medium volume threshold
                return 'MEDIUM'
            else:
                return 'LOW'
        except:
            return 'NORMAL'

    def _categorize_volatility(self, volatility: float) -> str:
        """ Categorize volatility level """
        if volatility > 10.0:
            return 'VERY_HIGH'
        elif volatility > 5.0:
            return 'HIGH'
        elif volatility > 2.0:
            return 'MEDIUM'
        elif volatility > 1.0:
            return 'LOW'
        else:
            return 'VERY_LOW'

    def _calculate_support_resistance(self, high: float, low: float, current: float) -> Dict[str, float]:
        """ Calculate basic support and resistance levels """
        try:
            # Simple support/resistance calculation
            range_size = high - low
            support = low + (range_size * 0.2)
            resistance = high - (range_size * 0.2)
            
            return {
                'support': round(support, 2),
                'resistance': round(resistance, 2),
                'range': round(range_size, 2)
            }
        except:
            return {
                'support': current * 0.95,
                'resistance': current * 1.05,
                'range': current * 0.1
            }

    def _update_market_history(self, context: Dict[str, Any]):
        """ Update market history with new context """
        try:
            timestamp = datetime.utcnow()
            self.market_history[timestamp] = context
            
            # Keep only last 100 entries
            if len(self.market_history) > 100:
                oldest_key = min(self.market_history.keys())
                del self.market_history[oldest_key]
                
        except Exception as e:
            logger.error(f"Error updating market history: {e}")

    def _get_default_context(self) -> Dict[str, Any]:
        """ Get default market context when analysis fails """
        return {
            'overall_trend': 'NEUTRAL',
            'trend_strength': 0.0,
            'market_volatility': 0.0,
            'volatility_level': 'UNKNOWN',
            'market_momentum': 0.0,
            'analyzed_symbols': 0,
            'symbol_breakdown': {'BULLISH': 0, 'BEARISH': 0, 'NEUTRAL': 0},
            'timestamp': datetime.utcnow().isoformat(),
            'confidence': 0.0,
            'status': 'default'
        }

    async def get_market_sentiment(self) -> str:
        """ Get current market sentiment """
        try:
            if not self.market_history:
                return "NEUTRAL"
            
            latest_context = list(self.market_history.values())[-1]
            return latest_context.get('overall_trend', 'NEUTRAL')
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return "NEUTRAL"

    def get_volatility_for_symbol(self, symbol: str) -> float:
        """ Get cached volatility for a symbol """
        return self.volatility_cache.get(symbol, 0.0)

    def is_high_volatility_period(self) -> bool:
        """ Check if current period has high volatility """
        try:
            if not self.market_history:
                return False
            
            latest_context = list(self.market_history.values())[-1]
            volatility_level = latest_context.get('volatility_level', 'UNKNOWN')
            return volatility_level in ['HIGH', 'VERY_HIGH']
        except:
            return False

    async def cleanup(self):
        """ Cleanup resources """
        self.market_history.clear()
        self.volatility_cache.clear()
        logger.info("🧹 MarketContextAnalyzer cleaned up")