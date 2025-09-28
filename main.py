"""
ChainPulse - Intelligent Technical Analysis System
Main entry point for the system
"""

import asyncio
import logging 
import signal 
import sys 
from pathlib import Path

# Add project root to path 
sys.path.append(str(Path(__file__).parent))

from core.pulse_engine import PulseEngine
from config.settings import settings  # Import the global instance
from utils.logging_config import setup_logging 

logger = logging.getLogger(__name__)

class ChainPulseApp:
    """Main ChainPulse Application"""

    def __init__(self):
        self.pulse_engine = None  # CORREGIDO: era 'true'
        self.running = False 

    async def initialize(self):
        """Initialize ChainPulse application"""
        try:
            logger.info("🚀 Starting ChainPulse - Intelligent Technical Analysis System")
            logger.info("📋 Loading configuration...")

            # Use global settings instance
            logger.info(f"✅ Configuration loaded - Analyzing {len(settings.SYMBOLS)} symbols")
            logger.info(f"🏆 Primary data source: {settings.get_primary_source().upper()}")

            # Initialize Pulse Engine 
            logger.info("🧠 Initializing Pulse Engine...")
            self.pulse_engine = PulseEngine(settings)

            initialization_success = await self.pulse_engine.initialize()
            if not initialization_success:
                logger.error("❌ Failed to initialize Pulse Engine")
                return False 

            logger.info("✅ Pulse initialization completed successfully")
            return True 

        except Exception as e:
            logger.error(f"❌ Critical error during initialization: {e}")
            return False 

    async def run(self):
        """Run Pulse main loop"""
        if not await self.initialize():
            logger.error("❌ Initialization failed, shutting down")
            return 

        self.running = True 
        logger.info("🎯 Pulse is now active - Market analysis started")

        try:
            # Setup signal handlers 
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            # Run main engine 
            await self.pulse_engine.run()

        except KeyboardInterrupt:
            logger.info("👋 Pulse stopped by user")
        except Exception as e:
            logger.error(f"❌ Critical error in main loop: {e}")
        finally:
            await self.shutdown()

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.running = False 

    async def shutdown(self):
        """Graceful shutdown"""  # CORREGIDO: era 'Craceful'
        logger.info("🛑 Initiating Pulse shutdown...")

        if self.pulse_engine:
            await self.pulse_engine.stop()

        logger.info("👋 Pulse shutdown completed")

async def main():
    """Main function"""
    # Setup logging first 
    setup_logging()

    # Create and run application 
    app = ChainPulseApp()
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())