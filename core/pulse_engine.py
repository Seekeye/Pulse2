""" Pulse Engine - Main System Coordinator """
""" Orchestrates all components: data collection, analysis, signals, notifications """

import asyncio 
import logging 
from typing import Dict, List, Optional 
from datetime import datetime, timedelta 

# IMPORTS MODIFICADOS PARA SOPORTAR MÚLTIPLES SOURCES
from data.collectors.multi_source_collector import MultiSourceCollector
from data.collectors.coinbase_collector import CoinbaseSource
from data.collectors.coingecko_simple import CoinGeckoSimpleSource
from data.collectors.binance_collector import BinanceSource
from data.collectors.coincap_collector import CoinCapSource
from data.collectors.cryptocompare_collector import CryptoCompareSource
from data.database_manager import DatabaseManager
from indicators.indicator_manager import IndicatorManager 
from signals.signal_generator import SignalGenerator 
from signals.signal_tracker import SignalTracker
from intelligence.market_context import MarketContextAnalyzer 
from notifications.telegram.telegram_bot import TelegramBot 
from utils.time_utils import get_current_timestamp

logger = logging.getLogger(__name__)

class PulseEngine:
    """ Main Pulse coordination engine """
    def __init__(self, settings):
        self.settings = settings 
        self.running = False 
        self.last_analysis = {}
        self.analysis_count = 0

        # Core components - MODIFICADO PARA SOPORTAR MÚLTIPLES COLLECTORS
        self.data_collector = None  # Will be CoinbaseSource or CoinGeckoSimpleSource
        self.indicator_manager: Optional[IndicatorManager] = None 
        self.signal_generator: Optional[SignalGenerator] = None
        self.market_analyzer: Optional[MarketContextAnalyzer] = None
        self.telegram_bot: Optional[TelegramBot] = None
        self.database_manager: Optional[DatabaseManager] = None
        self.signal_tracker: Optional[SignalTracker] = None 

        # Performance tracking 
        self.performance_stats = {
            'total_analysis': 0,
            'signals_generated': 0,
            'notifications_sent': 0,
            'errors': 0,
            'start_time': None
        }

        logger.info("PulseEngine initialized with configuration")
        logger.info(f"Data source: {self.settings.get_primary_source()}")
        logger.info(f"Target symbols: {', '.join(self.settings.SYMBOLS)}")
        logger.info(f"Analysis interval: {self.settings.ANALYSIS_INTERVAL}s")
    
    async def initialize(self) -> bool:
        """ Initialize all system components """
        try:
            logger.info("Starting Pulse component initialization...")
            self.performance_stats['start_time'] = datetime.utcnow()

            # 1. Initialize Data Collector - MULTI-SOURCE SYSTEM
            data_source = self.settings.get_primary_source()
            
            if data_source == "multi" and self.settings.ENABLE_MULTI_SOURCE:
                logger.info("Initializing Multi-Source data collection system...")
                self.data_collector = MultiSourceCollector(self.settings)
            elif data_source == "binance":
                logger.info("Initializing Binance data collection system...")
                binance_config = self.settings.get_binance_config()
                self.data_collector = BinanceSource(binance_config)
            elif data_source == "coincap":
                logger.info("Initializing CoinCap data collection system...")
                coincap_config = self.settings.get_coincap_config()
                self.data_collector = CoinCapSource(coincap_config)
            elif data_source == "cryptocompare":
                logger.info("Initializing CryptoCompare data collection system...")
                cryptocompare_config = self.settings.get_cryptocompare_config()
                self.data_collector = CryptoCompareSource(cryptocompare_config)
            elif data_source == "coingecko":
                logger.info("Initializing CoinGecko Simple data collection system...")
                coingecko_config = self.settings.get_coingecko_config()
                self.data_collector = CoinGeckoSimpleSource(coingecko_config)
            else:
                logger.info("Initializing Coinbase data collection system...")
                coinbase_config = self.settings.get_coinbase_config()
                self.data_collector = CoinbaseSource(coinbase_config)
            
            if not await self.data_collector.initialize():
                logger.error(f"Failed to initialize {data_source} data collector")
                return False 
            logger.info(f"✅ {data_source.title()} data collector ready")

            # 2. Initialize Market context Analyzer 
            logger.info("Initializing market context analyzer...")
            self.market_analyzer = MarketContextAnalyzer()
            await self.market_analyzer.initialize()
            logger.info("✅ Market analyzer ready")

            # 3. Initialize Indicator Manager
            logger.info("Initializing technical indicators...")
            self.indicator_manager = IndicatorManager()
            await self.indicator_manager.initialize()
            logger.info(f"✅ {self.indicator_manager.get_indicator_count()} indicators loaded")

            # 4. Initialize Signal Generator 
            logger.info("Initializing signal generation system...")
            self.signal_generator = SignalGenerator(
                self.indicator_manager,
                self.market_analyzer,
                self.settings
            ) 
            await self.signal_generator.initialize()
            logger.info("✅ Signal generator ready")

            # 5. Initialize Database Manager
            logger.info("Initializing database manager...")
            self.database_manager = DatabaseManager(self.settings.DATABASE_URL)
            if await self.database_manager.initialize():
                logger.info("✅ Database manager ready")
            else:
                logger.warning("⚠️ Database initialization failed - continuing without database storage")

            # 6. Initialize Signal Tracker
            logger.info("Initializing signal tracking system...")
            if self.database_manager:
                self.signal_tracker = SignalTracker(self.database_manager)
                logger.info("✅ Signal tracker ready")
            else:
                logger.warning("⚠️ Signal tracker disabled - no database connection")

            # 7. Initialize Telegram bot (if configured)
            if self.settings.TELEGRAM_BOT_TOKEN and self.settings.TELEGRAM_ENABLED:
                logger.info("Initializing Telegram notifications....")
                self.telegram_bot = TelegramBot(self.settings)
                if await self.telegram_bot.initialize():
                    logger.info("✅ Telegram bot connected and ready")
                else:
                    logger.warning("⚠️ Telegram bot initialization failed - continuing without notifications")
            else:
                logger.info("📱 Telegram notifications disabled")

            # Final validation 
            logger.info("Running system validation...")
            if await self._validate_system():
                logger.info("🎉 All components initialized successfully")
                logger.info("🚀 Pulse is ready for market analysis")
                return True 
            else:
                logger.error("❌ System validation failed")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to initialize Pulse Engine: {e}")
            return False

    async def _validate_system(self) -> bool:
        """ Validate all system components """
        try:
            # Test data collector connection
            data_source = self.settings.get_primary_source()
            logger.info(f"🔗 Testing {data_source} connection...")
            
            if not await self.data_collector.test_connection():
                logger.error(f"❌ {data_source} connection test failed")
                return False
            logger.info(f"✅ {data_source.title()} connection test successful")

            # Test data fetching with first symbol
            test_symbol = self.settings.SYMBOLS[0]
            test_data = await self.data_collector.get_symbol_data(test_symbol)
            
            if not test_data:
                logger.error(f"❌ Failed to fetch test data from {data_source}")
                return False

            logger.info(f"✅ Test data fetch successful for {test_symbol}")
            return True

        except Exception as e:
            logger.error(f"❌ System validation error: {e}")
            return False

    async def start(self):
        """ Start the main analysis loop """
        if self.running:
            logger.warning("⚠️ Pulse Engine is already running")
            return

        self.running = True
        logger.info("🔥 Pulse Engine started - Beginning market analysis")
        logger.info(f"👀 Monitoring {len(self.settings.SYMBOLS)} symbols")

        try:
            while self.running:
                await self._run_analysis_cycle()
                await asyncio.sleep(self.settings.ANALYSIS_INTERVAL)

        except Exception as e:
            logger.error(f"❌ Critical error in analysis loop: {e}")
            self.performance_stats['errors'] += 1
        finally:
            await self._cleanup()

    async def _run_analysis_cycle(self):
        """ Run a single analysis cycle """
        cycle_start = datetime.utcnow()
        self.analysis_count += 1
        
        try:
            # 1. Collect market data for all symbols
            market_data = {}
            market_data_full = {}  # Full data for indicators and signals
            successful_fetches = 0
            
            for symbol in self.settings.SYMBOLS:
                try:
                    data = await self.data_collector.get_symbol_data(symbol)
                    if data:
                        # Store full data for indicators and signals
                        market_data_full[symbol] = data
                        # Store only price for SignalTracker
                        market_data[symbol] = data.get('price', 0)
                        successful_fetches += 1
                        logger.info(f"💰 {symbol}: ${data.get('price', 0):.4f}")
                    else:
                        logger.warning(f"⚠️ No data received for {symbol}")
                except Exception as e:
                    logger.error(f"❌ Error fetching {symbol}: {e}")

            logger.info(f"📈 Market data collected for {successful_fetches} symbols")

            if not market_data:
                logger.warning("⚠️ No market data available - skipping analysis")
                return

            # 2. Analyze market context
            market_context = await self.market_analyzer.analyze_market_context(market_data_full)
            logger.info(f"📊 Market context: {market_context.get('trend', 'UNKNOWN')}")

            # 3. Calculate technical indicators for each symbol
            all_indicators = {}
            for symbol, data in market_data_full.items():
                try:
                    # Get historical data for indicators
                    historical_data = await self.data_collector.get_historical_data(symbol)
                    if historical_data:
                        indicators = await self.indicator_manager.calculate_indicators(symbol, historical_data, market_context)
                        all_indicators[symbol] = indicators
                        logger.info(f"📊 {symbol}: {len(indicators)} indicators calculated")
                    else:
                        logger.warning(f"⚠️ No historical data for {symbol}")
                except Exception as e:
                    logger.error(f"❌ Error calculating indicators for {symbol}: {e}")

            # 4. Generate trading signals
            signals = await self.signal_generator.generate_signals(
                market_data_full, 
                all_indicators, 
                market_context
            )

            if signals:
                logger.info(f"🎯 {len(signals)} trading signals generated")
                for signal in signals:
                    logger.info(f"📡 {signal.symbol}: {signal.direction.value} - {signal.confidence:.1f}%")

            # 5. Save signals to database
            if signals and self.database_manager:
                logger.info(f"💾 Saving {len(signals)} signals to database...")
                for signal in signals:
                    try:
                        await self.database_manager.save_signal(signal)
                        logger.debug(f"✅ Signal saved to database: {signal.symbol}")
                    except Exception as e:
                        logger.error(f"❌ Error saving signal to database: {e}")
                        continue

            # 6. Add signals to tracking system
            if signals and self.signal_tracker:
                logger.info(f"🎯 Adding {len(signals)} signals to tracking...")
                for signal in signals:
                    try:
                        await self.signal_tracker.add_signal(signal)
                        logger.debug(f"✅ Signal added to tracking: {signal.symbol}")
                    except Exception as e:
                        logger.error(f"❌ Error adding signal to tracking: {e}")
                        continue

            # 7. Update tracking with current prices
            if self.signal_tracker and market_data:
                try:
                    tracking_results = await self.signal_tracker.update_prices(market_data)
                    if tracking_results:
                        logger.info(f"📊 {len(tracking_results)} tracking events detected")
                        for result in tracking_results:
                            logger.info(f"🎯 {result.message}")
                            
                            # Send tracking notifications to Telegram
                            if self.telegram_bot:
                                await self._send_tracking_notification(result)
                                
                except Exception as e:
                    logger.error(f"❌ Error updating signal tracking: {e}")

            # 8. Send notifications if signals generated
            if signals and self.telegram_bot:
                logger.info(f"📱 Sending {len(signals)} signals to Telegram...")
                for signal in signals:
                    try:
                        await self.telegram_bot.send_signal(signal)
                        self.performance_stats['notifications_sent'] += 1
                        
                        # Mark signal as sent to Telegram in database
                        if self.database_manager:
                            await self.database_manager.mark_signal_sent_to_telegram(signal.signal_id)
                        
                        logger.info(f"✅ Signal sent to Telegram: {signal.symbol}")
                    except Exception as e:
                        logger.error(f"❌ Error sending signal to Telegram: {e}")
                        continue

            # Update performance stats
            self.performance_stats['total_analysis'] += 1
            self.performance_stats['signals_generated'] += len(signals)

            # Calculate cycle time
            cycle_time = (datetime.utcnow() - cycle_start).total_seconds()
            logger.info(f"✅ Analysis cycle #{self.analysis_count} completed in {cycle_time:.2f}s")

            # Log performance summary every 10 cycles
            if self.analysis_count % 10 == 0:
                await self._log_performance_summary()

        except Exception as e:
            logger.error(f"❌ Error in analysis cycle: {e}")
            self.performance_stats['errors'] += 1

    async def _log_performance_summary(self):
        """ Log performance summary """
        uptime = datetime.utcnow() - self.performance_stats['start_time']
        
        logger.info("📊 === PERFORMANCE SUMMARY ===")
        logger.info(f"⏱️ Uptime: {uptime}")
        logger.info(f"🔄 Total Analysis: {self.performance_stats['total_analysis']}")
        logger.info(f"🎯 Signals Generated: {self.performance_stats['signals_generated']}")
        logger.info(f"📱 Notifications Sent: {self.performance_stats['notifications_sent']}")
        logger.info(f"❌ Errors: {self.performance_stats['errors']}")
        logger.info("==============================")

    async def stop(self):
        """ Stop the analysis loop """
        logger.info("🛑 Stopping Pulse Engine...")
        self.running = False

    async def _cleanup(self):
        """ Cleanup resources """
        logger.info("🧹 Cleaning up Pulse Engine resources...")
        
        try:
            if self.data_collector:
                await self.data_collector.cleanup()
            
            if self.telegram_bot:
                await self.telegram_bot.cleanup()
            
            if self.database_manager:
                await self.database_manager.close()
                
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
        
        logger.info("✅ Pulse Engine cleanup completed")
    
    async def _send_tracking_notification(self, tracking_result):
        """ Send tracking notification to Telegram """
        try:
            if not self.telegram_bot:
                return
            
            # Formatear mensaje de tracking
            emoji_map = {
                "tp1_hit": "🎯",
                "tp2_hit": "🎯🎯", 
                "tp3_hit": "🎯🎯🎯",
                "stop_loss_hit": "🛡️",
                "signal_closed": "✅",
                "signal_reinforced": "💪",
                "signal_conflicted": "⚠️",
                "signal_replaced": "🔄"
            }
            
            emoji = emoji_map.get(tracking_result.event.value, "📊")
            
            message = f"""
{emoji} **TRACKING UPDATE**

**{tracking_result.symbol}** - {tracking_result.event.value.upper()}

💰 **Precio Actual:** ${tracking_result.current_price:.4f}
🎯 **Precio Objetivo:** ${tracking_result.target_price:.4f}
📊 **P&L:** {tracking_result.profit_loss_pct:+.1f}%

{tracking_result.message}

⏰ {tracking_result.timestamp.strftime('%H:%M:%S')}
            """.strip()
            
            await self.telegram_bot.send_message(message)
            logger.info(f"✅ Tracking notification sent: {tracking_result.symbol}")
            
        except Exception as e:
            logger.error(f"❌ Error sending tracking notification: {e}")

    async def run(self):
        """ Main run method - Entry point for the engine """
        logger.info("🚀 Starting Pulse Engine main loop...")
        await self.start()