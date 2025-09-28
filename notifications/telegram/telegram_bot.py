""" Telegram bot - Intelligent signal notification """
""" Sends formatted trading signals and status updates via Telegram """

from doctest import ELLIPSIS_MARKER
import logging 
import asyncio 
from typing import Optional, List, Dict, Any 
from datetime import datetime 
import aiohttp 

from signals.signal import Signal 

logger = logging.getLogger(__name__)

class TelegramBot: 
    """ Telegram bot for Pulse notifications """

    def __init__(self, settings):
        self.settings = settings
        self.bot_token = settings.TELEGRAM_BOT_TOKEN 
        self.chat_id = settings.TELEGRAM_CHAT_ID 
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        self.session = None 
        self.is_initialized = False
        self.message_queue = []
        self.rate_limit_delay = 1.0 # 1 second between messages 
        self.last_message_time = 0

        # Statistics
        self.stats = {
            'messages_sent': 0,
            'signals_sent': 0,
            'errors': 0,
            'start_time': datetime.utcnow()
        }

        logger.info("TelegramBot created")
        if not self.bot_token:
            logger.warning("No Telegram bot token configured")
        if not self.chat_id:
            logger.warning("No Telegram chat ID configured")

    async def initialize(self) -> bool:
        """ Initialize Telegram bot"""
        try:
            if not self.bot_token or not self.chat_id:
                logger.error("Telegram bot token or chat ID not configured")
                return False 

            logger.info("Initializing Telegram bot...")

            # Create aiohttp session 
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)

            # Test bot connection 
            if await self._test_bot_connection():
                self.is_initialized = True
                logger.info("Telegram bot initialized successfully")

                # Send startup message
                await self._send_startup_message()
                return True 
            else:
                logger.error("Telegram bot connection test failed")
                return False 
        
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            return False 

    async def _test_bot_connection(self) -> bool:
        """ Test Telegram bot connection """
        try:
            logger.debug("Testing Telegram bot connection...")

            url = f"{self.base_url}/getMe"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        bot_info = data.get('result', {})
                        bot_name = bot_info.get('username', 'Unknown')
                        logger.info(f"Connected to Telegram bot: @{bot_name}")
                        return True 
                    else:
                        logger.error(f"Telegram API error: {data.get('description', 'Unknown error')}")
                        return False 
                else:
                    logger.error(f"Telegram API returned status {response.status}")
                    return False 
        
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False 

    async def send_signal(self, signal: Signal) -> bool:
        """ Send trending signal to Telegram """
        try:
            if not self.is_initialized:
                logger.warning("Telegram bot not initialized")
                return False 
            
            logger.info(f"Sending signal or {signal.symbol} via Telegram...")

            # Format signal message
            message = signal.to_telegram_message()

            # Send message 
            success = await self._send_message(message, parse_mode='Markdown')

            if success:
                self.stats['signal_sent'] += 1
                logger.info(f"Signal sent for {signal.symbol}: {signal.direction.value}")
            else:
                logger.error(f"Failed to send signal for {signal.symbol}")

            return success 
        
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            self.stats['errors'] += 1
            return False 

    async def send_status_update(self, status_data: Dict[str, Any]) -> bool:
        """ Send system status update """
        try:
            if not self.is_initialized:
                return False

            logger.debug("Sending status update...")

            message = self._format_status_message(status_data)
            success = await self._send_message(message, parse_mode='Markdown')

            if success: 
                logger.debug("Stauts update sent")

            return success 

        except Exception as e:
            logger.error(f"Error sending status update: {e}")
            return False 

    async def send_market_summary(self, market_context: Dict[str, Any]) -> bool:
        """ Sed market summary """
        try:
            if not self.is_initialized:
                return False 

            logger.debug("Sending market summary...")

            message = self._format_market_summary(market_context)
            success = await self._send_message(message, parse_mode='Markdown')

            if success: 
                logger.debug("Market summary sent")

            return success 
        
        except Exception as e:
            logger.error(f"Error sending market summary: {e}")
            return False 

    async def _send_message(self, text: str, parse_mode: str = 'Markdown') -> bool:
        """ Send message to Telegram with rate limiting """
        try:
            # Rate limitng 
            await self._rate_limit()

            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }

            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('ok'):
                        self.stats['messages_sent'] += 1
                        logger.info(f"✅ Telegram message sent successfully")
                        return True 
                    else:
                        error_desc = data.get('description', 'Unknown error')
                        logger.error(f"Telegram API error: {error_desc}")
                        return False
                else:
                    logger.error(f"Telegram HTTP error: {response.status}")
                    return False 
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            self.stats['errors'] += 1
            return False 

    async def _rate_limit(self):
        """ Implement rate limiting for Telegram messages """
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_message_time 

        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            await asyncio.sleep(sleep_time)

        self.last_message_time = asyncio.get_event_loop().time()

    async def _send_startup_message(self):
        """ Send startup notification """
        try:
            message = """
🚀 **Pulse Started**

🧠 Intelligent Technical Analysis System
📊 Monitoring crypto markets for trading opportunities
🎯 Dynamic TP/SL levels based on market context

✅ System Status: **ACTIVE**
📈 Ready to analyze signals

#Pulse #Started
            """ 

            await self._send_message(message.strip())
            logger.info("Startup message sent")
        
        except Exception as e:
            logger.error(f"Error sending startup message: {e}")
        
    def _format_status_message(self, status_data: Dict[str, Any]) -> str:
        """ Format system status message """
        try:
            uptime = status_data.get('uptime', 'Unknown')
            signals_generated = status_data.get('signals_generated', 0)
            symbols_monitored = status_data.get('symbols_monitored', 0)
            last_analysis = status_data.get('last_analysis', 'Never')

            message = f"""
📊 **ChainPulse Status Update**

⏱️ **Uptime:** {uptime}
🎯 **Signals Generated:** {signals_generated}
📈 **Symbols Monitored:** {symbols_monitored}
🔍 **Last Analysis:** {last_analysis}

✅ System running normally

#ChainPulse #Status
            """

            return message.strip()

        except Exception as e:
            logger.error(f"Error formatting status message: {e}")
            return "Pulse Status: System running"

    def _format_market_summary(self, market_context: Dict[str, Any]) -> str:
        """ Format market summary message """
        try:
            overall_trend = market_context.get('overall_trend', 'Unknown')
            sentiment = market_context.get('market_sentiment', 'Unknown')
            volatility = market_context.get('volatility', 'Unknown')
            symbols_analyzed = market_context.get('symbols_analyzed', 0)
            bullish_count = market_context.get('bullish_symbols', 0)
            bearish_count = market_context.get('bearish_symbols', 0)

            # Trend emoji 
            trend_emoji = {
                'STRONG_UPTREND': '🚀📈',
                'UPTREND': '📈',
                'WEAK_UPTREND': '↗️',
                'STRONG_DOWNTREND': '📉💥',
                'DOWNTREND': '📉',
                'WEAK_DOWNTREND': '↘️',
                'NEUTRAL': '↔️'
            }.get(overall_trend, '📊')

            # Sentiment emoji
            sentiment_emoji = {
                'VERY_BULLISH': '🟢🟢',
                'BULLISH': '🟢',
                'NEUTRAL': '🟡',
                'BEARISH': '🔴',
                'VERY_BEARISH': '🔴🔴'
            }.get(sentiment, '🟡')
            
            message = f"""
🌊 **Market Summary**

{trend_emoji} **Overall Trend:** {overall_trend.replace('_', ' ').title()}
{sentiment_emoji} **Market Sentiment:** {sentiment.replace('_', ' ').title()}
📊 **Volatility:** {volatility}

📈 **Bullish Symbols:** {bullish_count}
📉 **Bearish Symbols:** {bearish_count}
📊 **Total Analyzed:** {symbols_analyzed}

#ChainPulse #MarketSummary
            """
            
            return message.strip()
            
        except Exception as e:
            logger.error(f"❌ Error formatting market summary: {e}")
            return "🌊 Market Summary: Analysis complete"
    
    async def stop(self):
        """Stop Telegram bot"""
        try:
            logger.info("🛑 Stopping Telegram bot...")
            
            # Send shutdown message
            if self.is_initialized:
                shutdown_message = """
🛑 **ChainPulse Stopped**

📊 Session Statistics:
📱 Messages Sent: {messages_sent}
🚨 Signals Sent: {signals_sent}
❌ Errors: {errors}
⏱️ Session Duration: {duration}

👋 System shutdown complete

#ChainPulse #Stopped
                """.format(
                    messages_sent=self.stats['messages_sent'],
                    signals_sent=self.stats['signals_sent'],
                    errors=self.stats['errors'],
                    duration=str(datetime.utcnow() - self.stats['start_time']).split('.')[0]
                )
                
                await self._send_message(shutdown_message.strip())
            
            # Close session
            if self.session:
                await self.session.close()
                logger.info("🔌 Telegram session closed")
            
            self.is_initialized = False
            logger.info("✅ Telegram bot stopped")
            
        except Exception as e:
            logger.error(f"❌ Error stopping Telegram bot: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            **self.stats,
            'uptime': datetime.utcnow() - self.stats['start_time'],
            'is_initialized': self.is_initialized
        } 
            