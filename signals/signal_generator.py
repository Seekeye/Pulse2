""" Signal Generator - Core intelligent signal generation system """
""" Combines indicators, market context, and dynamic TP/SL calculation """

import logging 
import asyncio 
from typing import Dict, List, Optional, Any 
from datetime import datetime, timedelta 

from .signal import Signal, SignalDirection, MarketContext, create_buy_signal, create_sell_signal 

logger = logging.getLogger(__name__)

class SignalGenerator:
    """ Intelligent signal generation system """

    def __init__(self, indicator_manager, market_analyzer, settings):
        self.indicator_manager = indicator_manager
        self.market_analyzer = market_analyzer 
        self.settings = settings 

        # Signal generation parameters 
        self.min_confidence = settings.MIN_CONFIDENCE 
        self.min_risk_reward = settings.RISK_REWARD_MIN 
        self.max_signals_per_hour = settings.MAX_SIGNALS_PER_HOUR 

        # Tracking 
        self.recent_signals = []
        self.signal_history = {}
        self.symbol_cooldowns = {}  # Track last signal time per symbol

        logger.info("SignalGenerator initialized")
        logger.info(f"   Min confidence: {self.min_confidence}%")
        logger.info(f"   Min risk/reward: {self.min_risk_reward}")
        logger.info(f"   Max signals/hour: {self.max_signals_per_hour}")

    async def initialize(self) -> bool:
        """ Initialize signal generator """
        try:
            logger.info("Initializing signal generation system...")
            
            # Validate dependencies 
            if not self.indicator_manager.is_initialized:
                logger.error("IndicatorManager not initialized")
                return False 
            
            logger.info("Signal generator ready")
            return True 
        
        except Exception as e:
            logger.error(f"Error initializing signal generator: {e}")
            return False 

    async def generate_signals(self, market_data: Dict, indicators: Dict, market_context: Dict) -> List[Signal]:
        """ Generate trading signals for all symbols """
        try:
            logger.debug("Starting signal generation process...")

            all_signals = []

            # Check rate limiting 
            if not self._can_generate_signals():
                logger.info("Signal rate limit reached - skipping generation")
                return []

            # Generate signals for each symbol
            for symbol, symbol_data in market_data.items():
                try: 
                    # Check cooldown for this symbol
                    if not self._can_generate_signal_for_symbol(symbol):
                        logger.debug(f"Symbol {symbol} in cooldown - skipping")
                        continue
                    
                    symbol_indicators = indicators.get(symbol, {})
                    if not symbol_indicators:
                        logger.warning(f"No indicators available for {symbol}")
                        continue 

                    # Generate signal for this symbol 
                    signal = await self._generate_symbol_signal(symbol, symbol_data, symbol_indicators, market_context)
                    if signal:
                        all_signals.append(signal)
                        # Update cooldown for this symbol
                        self.symbol_cooldowns[symbol] = datetime.utcnow()
                        logger.info(f"Signal generated for {symbol}: {signal.direction.value} (confidence: {signal.confidence:.1f}%)")
                    else:
                        logger.debug(f"No signal generated for {symbol}")
                
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {e}")
                    continue 

            # Update signal tracking 
            self._update_signal_tracking(all_signals)

            logger.info(f"Signal generation completed: {len(all_signals)} signals generated")
            return all_signals 
        
        except Exception as e:
            logger.error(f"Error in signal generation: {e}")
            return []

    async def _generate_symbol_signal(self, symbol: str, market_data: Dict, indicators: Dict, market_context: Dict) -> Optional[Signal]:
        """ Generate signal for a specific symbol """
        try:
            logger.debug(f"Analyzing {symbol} for signal generation...")

            current_price = float(market_data.get('price', 0))
            if current_price == 0:
                logger.warning(f"Invalid price for {symbol}")
                return None 

            # Get composite inidcator analysis 
            composite = indicators.get('composite', {})
            if not composite:
                logger.warning(f"No composite analysis for {symbol}")
                return None 

            overall_score = composite.get('overall_score', 50)
            overall_bias = composite.get('overall_bias', 'NEUTRAL')
            contributing_indicators = composite.get('contributing_indicators', [])
            indicator_scores = composite.get('indicator_scores', {})

            # Determine signal direction 
            signal_direction = None 
            base_confidence = 0.0

            # LÓGICA MEJORADA - MENOS EXIGENTE
            if overall_bias in ['STRONG_BULLISH', 'BULLISH'] and overall_score > 45:  # REDUCIDO DE 60 A 45
                signal_direction = SignalDirection.BUY 
                base_confidence = overall_score 
            elif overall_bias in ['STRONG_BEARISH', 'BEARISH'] and overall_score < 55:  # REDUCIDO DE 40 A 55
                signal_direction = SignalDirection.SELL
                base_confidence = 100 - overall_score # Invert for sell signals
            # AÑADIR SEÑALES NEUTRALES CON ALTA CONFIANZA
            elif overall_bias == 'NEUTRAL' and overall_score > 70:  # NUEVO: Señales en mercado neutral
                signal_direction = SignalDirection.BUY if overall_score > 75 else SignalDirection.SELL
                base_confidence = overall_score

            if not signal_direction:
                logger.debug(f"{symbol}: No clear signal direction (bias: {overall_bias}, score: {overall_score:.1f})")
                return None 

            # Calculate confidence with market context 
            final_confidence = await self._calculate_signal_confidence(base_confidence, market_context, indicators, market_data)

            # Check minimum confidence threshold - CONVERSIÓN A PORCENTAJE
            min_confidence_percent = self.min_confidence * 100
            if final_confidence < min_confidence_percent:
                logger.debug(f"{symbol}: Confidence too low ({final_confidence:.1f}% < {min_confidence_percent:.1f}%)")
                return None 

            # Calculate dynamic TP/SL levels 
            levels = await self._calculate_dynamic_levels(symbol, current_price, signal_direction, market_context, indicators)

            # Calculate risk/reward ratio 
            risk_reward = self._calculate_risk_reward(current_price, levels, signal_direction)

            # Check minimum risk/reward threshold 
            if risk_reward < self.min_risk_reward:
                logger.debug(f"{symbol}: Risk/reward too low ({risk_reward:.2f} < {self.min_risk_reward})")
                return None 

            # Determine market context enum 
            market_context_enum = self._get_market_context_enum(market_context)

            # Generate reasoning
            reasoning = self._generate_reasoning(overall_bias, contributing_indicators, market_context)

            # Create signal 
            signal = Signal(
                symbol=symbol,
                direction=signal_direction,
                entry_price=current_price,
                current_price=current_price,
                tp1 = levels['tp1'],
                tp2=levels['tp2'],
                tp3=levels['tp3'],
                stop_loss=levels['stop_loss'],
                confidence=final_confidence,
                risk_reward_ratio=risk_reward,
                market_context=market_context_enum,
                contributing_indicators=contributing_indicators,
                indicator_scores = indicator_scores,
                strategy = "intelligent_multi_indicator",
                timeframe="1h",
                expected_duration=self._determine_duration(market_context, indicators),
                reasoning=reasoning
            )

            logger.info(f"{symbol} signal created: {signal_direction.value} @ ${current_price:.4f} (confidence: {final_confidence:.1f}%)")
            return signal 

        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None 

    async def _calculate_signal_confidence(self, base_confidence: float, market_context: Dict, indicators: Dict, market_data: Dict) -> float:
        """ Calculate final signal confidence with market context adjustment """
        try:
            confidence = base_confidence

            # Market context adjustments
            market_trend = market_context.get('overall_trend', 'NEUTRAL')
            market_volatility = market_context.get('volatility', 'MEDIUM')

            # Boost confidence in trending markets
            if market_trend in ['STRONG_UPTREND', 'STRONG_DOWNTREND']:
                confidence += 10
                logger.debug("Confidence boost: Strong trending market (+10)")
            elif market_trend in ["UPTREND", "DOWNTREND"]:
                confidence += 5
                logger.debug("Confidence boost: Trending market (+5)")

            # Adjust for volatility 
            if market_volatility == 'LOW':
                confidence += 5 # More predictable 
                logger.debug("Confidence boost: Low volatility (+5)")
            elif market_volatility == 'HIGH':
                confidence -= 10 # Less predictable 
                logger.debug("Confidence penalty: High volatility (-10)")

            # Volume confirmation
            volume_24h = market_data.get('volume', 0)
            avg_volume = market_data.get('avg_volume', volume_24h) # Fallback to current if no avg 

            if volume_24h > avg_volume * 1.5:
                confidence += 8
                logger.debug("Confidence boost: High volume (+8)")
            elif volume_24h < avg_volume * 0.5:
                confidence -= 5
                logger.debug("Confidence penalty: Low volume (-5)")

            # Indicator consensus (more indicators agreeing = higher confidence) - MEJORADO
            composite = indicators.get('composite', {})
            contributing_count = len(composite.get('contributing_indicators', []))
            total_indicators = composite.get('total_indicators', 1)

            consensus_ratio = contributing_count / max(total_indicators, 1)
            if consensus_ratio > 0.6:  # REDUCIDO DE 0.7 A 0.6
                confidence += 15  # AUMENTADO DE 10 A 15
                logger.debug(f"Confidence boost: Strong consensus ({consensus_ratio:.1%}) (+15)")
            elif consensus_ratio > 0.4:  # REDUCIDO DE 0.5 A 0.4
                confidence += 8  # AUMENTADO DE 5 A 8
                logger.debug(f"Confidence boost: Good consensus ({consensus_ratio:.1%}) (+8)")
            elif consensus_ratio > 0.2:  # NUEVO: Consenso mínimo
                confidence += 3
                logger.debug(f"Confidence boost: Minimal consensus ({consensus_ratio:.1%}) (+3)")

            # Ensure confidence stays within bounds 
            final_confidence = max(0, min(100, confidence))

            logger.debug(f"Confidence calculation: {base_confidence:.1f} → {final_confidence:.1f}")
            return final_confidence
        
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return base_confidence

    async def _calculate_dynamic_levels(self, symbol:str, entry_price: float, direction: SignalDirection, market_context: Dict, indicators: Dict) -> Dict[str, float]:
        """ Calculate dynamic TP and SL levels based on market context """
        try:
            logger.debug(f"Calculating dynamic levels for {symbol}...")

            # Base percentages (will be adjusted)
            base_tp_percentages = [1.5, 3.0, 5.0] # TP1, TP2, TP3
            base_sl_percentage = 1.0

            # Market context adjustment 
            volatility = market_context.get('volatility', 'MEDIUM')
            trend_strength = market_context.get('trend_strength', 'MEDIUM')

            # Volatility adjustment 
            volatility_multiplier = {
                'LOW': 0.7,
                'MEDIUM': 1.0,
                'HIGH': 1.5,
                'EXTREME': 2.0
            }.get(volatility, 1.0)

            # Trend strength adjustment
            trend_multiplier = {
                'WEAK': 0.8,
                'MEDIUM': 1.0,
                'STRONG': 1.3
            }.get(trend_strength, 1.0)

            # Apply multipliers
            adjusted_tp_percentages = [tp * volatility_multiplier * trend_multiplier for tp in base_tp_percentages]
            adjusted_sl_percentage = base_sl_percentage * volatility_multiplier * 0.8 # SL less agrassive 

            # Calculate actual levels 
            if direction == SignalDirection.BUY:
                tp1 = entry_price * (1 + adjusted_tp_percentages[0] / 100)
                tp2 = entry_price * (1 + adjusted_tp_percentages[1] / 100)
                tp3 = entry_price * (1 + adjusted_tp_percentages[2] / 100)
                stop_loss = entry_price * (1 - adjusted_sl_percentage / 100)
            else:
                tp1 = entry_price * (1 - adjusted_tp_percentages[0] / 100)
                tp2 = entry_price * (1 - adjusted_tp_percentages[1] / 100)
                tp3 = entry_price * (1 - adjusted_tp_percentages[2] / 100)
                stop_loss = entry_price * (1 + adjusted_sl_percentage / 100)

            levels = {
               'tp1': tp1,
               'tp2': tp2,
               'tp3': tp3,
               'stop_loss': stop_loss 
            }

            logger.debug(f"{symbol} levels: TP1=${tp1:.4f}, TP2=${tp2:.4f}, TP3=${tp3:.4f}, SL=${stop_loss:.4f}")
            return levels 
        
        except Exception as e:
            logger.error(f"Error calculating levels for {symbol}: {e}")
            # Return safe default levels 
            return {
                'tp1': entry_price * 1.02 if direction == SignalDirection.BUY else entry_price * 0.98,
                'tp2': entry_price * 1.04 if direction == SignalDirection.BUY else entry_price * 0.96,
                'tp3': entry_price * 1.06 if direction == SignalDirection.BUY else entry_price * 0.94,
                'stop_loss': entry_price * 0.99 if direction == SignalDirection.BUY else entry_price * 1.01,
            }

    def _calculate_risk_reward(self, entry_price: float, levels: Dict, direction: SignalDirection) -> float:
        """ Calculate risk/reward ratio """
        try:
            tp1 = levels['tp1']
            stop_loss = levels['stop_loss']

            if direction == SignalDirection.BUY:
                potential_profit = tp1 - entry_price
                potential_loss = entry_price - stop_loss 
            else:
                potential_profit = entry_price - tp1
                potential_loss = stop_loss - entry_price

            if potential_loss <= 0:
                return 0.0

            risk_reward = potential_profit / potential_loss
            return max(0.0, risk_reward)

        except Exception as e:
            logger.error(f"Error calculating risk/reward: {e}")
            return 0.0

    def _get_market_context_enum(self, market_context: Dict) -> MarketContext:
        """ Convert market context to enum """
        trend = market_context.get('overall_trend', 'NEUTRAL')
        volatility = market_context.get('volatility', 'MEDIUM')

        if 'UPTREND' in trend:
            return MarketContext.TRENDING_UP
        elif 'DOWNTREND' in trend:
            return MarketContext.TRENDING_DOWN
        elif volatility in ['HIGH', 'EXTREME']:
            return MarketContext.VOLATILE
        else:
            return MarketContext.SIDEWAYS 

    def _generate_reasoning(self, bias: str, indicators: List[str], market_context: Dict) -> str:
        """ Generate human-readeable reasoning for the signal """
        try:
            trend = market_context.get('overall_trend', 'neutral')
            volatility = market_context.get('volatility', 'medium')

            reasoning_parts = []

            # Main bias 
            if bias == 'STRONG_BULLISH':
                reasoning_parts.append("Strong bullish momentum detected")
            elif bias == "BULLISH":
                reasoning_parts.append("Bullish signals emerging")
            elif bias == "STRONG_BEARISH":
                reasoning_parts.append("Strong bearish pressure identified")
            elif bias == "BEARISH":
                reasoning_parts.append("Bearish indicators aligning")

            # Market context 
            if 'UPTREND' in trend:
                reasoning_parts.append("supported by upward market trend")
            elif 'DOWNTREND' in trend:
                reasoning_parts.append("confirmed by downward market trend")

            # Key indicators 
            if indicators:
                key_indicators = indicators[:2] # Top 2 indicators
                reasoning_parts.append(f"with {', '.join(key_indicators)} showing strength")

            # Volatility context 
            if volatility == 'LOW':
                reasoning_parts.append("in stable market conditions")
            elif volatility == 'HIGH':
                reasoning_parts.append("despite elevated volatility")

            return ". ".join(reasoning_parts).capitalize() + "."

        except Exception as e:
            logger.error(f"Error generating reasoning: {e}")

        return "Technical analysis indicates trading opportunity."

    def _determine_duration(self, market_context: Dict, indicators: Dict) -> str:
        """ Determine expected signal dureation """
        try:
            trend_strength = market_context.get('trend_strength', 'MEDIUM')
            volatility = market_context.get('volatility', 'MEDIUM')

            if trend_strength == 'STRONG' and volatility == 'LOW':
                return "LONG" # 1-7 days 
            elif volatility == 'HIGH':
                return "SHORT" # 1-4 hours
            else:
                return "MEDIUM" # 4-24 hours 

        except Exception as e:
            logger.error(f"Error determining duration: {e}")
            return "MEDIUM"

    def _can_generate_signals(self) -> bool:
        """ Check if we can generate more signals (rate limiting) """
        try:
            current_time = datetime.utcnow()
            one_hour_ago = current_time - timedelta(hours=1)

            # Count recent signals
            recent_count = len([s for s in self.recent_signals if s.timestamp > one_hour_ago])
            can_generate = recent_count < self.max_signals_per_hour 

            if not can_generate:
                logger.info(f"Rate limit: {recent_count}/{self.max_signals_per_hour} signals in last hour")

            return can_generate
        
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True # Allow generation on error

    def _can_generate_signal_for_symbol(self, symbol: str) -> bool:
        """ Check if we can generate a signal for a specific symbol (cooldown) """
        try:
            current_time = datetime.utcnow()
            cooldown_minutes = 5  # 5 minutes cooldown between signals for same symbol
            
            if symbol in self.symbol_cooldowns:
                last_signal_time = self.symbol_cooldowns[symbol]
                time_since_last = current_time - last_signal_time
                
                if time_since_last.total_seconds() < cooldown_minutes * 60:
                    remaining_minutes = cooldown_minutes - (time_since_last.total_seconds() / 60)
                    logger.debug(f"Cooldown active for {symbol}: {remaining_minutes:.1f} minutes remaining")
                    return False
            
            return True
        
        except Exception as e:
            logger.error(f"Error checking symbol cooldown: {e}")
            return True

    def _update_signal_tracking(self, new_signals: List[Signal]):
        """ Update signal tracking for rate limiting """
        try:
            # Add new signals to tracking 
            self.recent_signals.extend(new_signals)

            # Clean old signal (keep last 24 hours)
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(hours=24)

            self.recent_signals = [s for s in self.recent_signals if s.timestamp > cutoff_time]
            logger.debug(f"Signal tracking updated: {len(self.recent_signals)} recent signals")
        
        except Exception as e:
            logger.error(f"Error updating signal tracking: {e}")

