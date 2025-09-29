"""
ChainPulse Settings - Complete Configuration
"""
import os
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class Settings:
    """Main ChainPulse configuration"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN: str = "7768754099:AAGApzz5V-MQhhUv9VG9QLV4U4TIcJpLIL8"
    TELEGRAM_CHAT_ID: str = "1852997724"
    TELEGRAM_ENABLED: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///chainpulse.db"
    DATABASE_ECHO: bool = False
    
    # Data Source Configuration - MULTI-SOURCE SYSTEM
    DATA_SOURCE: str = "multi"  # "multi", "binance", "coincap", "cryptocompare", "coingecko", "coinbase"
    ENABLE_MULTI_SOURCE: bool = True  # Enable intelligent fallback system
    
    # Coinbase Configuration (mantenido para compatibilidad)
    COINBASE_API_KEY: str = os.getenv("COINBASE_API_KEY", "")
    COINBASE_API_SECRET: str = os.getenv("COINBASE_API_SECRET", "")
    COINBASE_PASSPHRASE: str = os.getenv("COINBASE_PASSPHRASE", "")
    COINBASE_SANDBOX: bool = False
    
    # CoinGecko Configuration - NUEVO
    COINGECKO_API_KEY: str = os.getenv("COINGECKO_API_KEY", "")  # Optional, for pro features
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    
    # Binance Configuration - NUEVO
    BINANCE_BASE_URL: str = "https://api.binance.com/api/v3"
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")  # Optional for basic data
    
    # CoinCap Configuration - NUEVO
    COINCAP_BASE_URL: str = "https://api.coincap.io/v2"
    
    # CryptoCompare Configuration - NUEVO
    CRYPTOCOMPARE_BASE_URL: str = "https://min-api.cryptocompare.com/data"
    CRYPTOCOMPARE_API_KEY: str = os.getenv("CRYPTOCOMPARE_API_KEY", "")  # Optional for free tier
    
    # Trading Configuration - SÍMBOLOS EXPANDIDOS
    SYMBOLS: List[str] = ["BTC-USD", "ETH-USD", "ADA-USD", "MATIC-USD", "SOL-USD", "LINK-USD"]
    DEFAULT_TIMEFRAME: str = "1h"
    MAX_POSITIONS: int = 3
    
    # Risk Management
    MAX_RISK_PER_TRADE: float = 0.02
    STOP_LOSS_PERCENTAGE: float = 0.05
    TAKE_PROFIT_PERCENTAGE: float = 0.10
    
    # Indicator Settings
    SMA_PERIODS: List[int] = [20, 50, 200]
    EMA_PERIODS: List[int] = [12, 26]
    RSI_PERIOD: int = 14
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_ENABLED: bool = True
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "chainpulse.log"
    
    # Analysis Configuration
    ANALYSIS_INTERVAL: int = 300  # 5 minutes
    DATA_FETCH_INTERVAL: int = 60  # 1 minute
    SIGNAL_COOLDOWN: int = 900  # 15 minutes
    
    # Performance Configuration
    MAX_CONCURRENT_REQUESTS: int = 10
    REQUEST_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    
    # Data Storage Configuration
    MAX_CANDLES_STORED: int = 1000
    DATA_CLEANUP_INTERVAL: int = 3600  # 1 hour
    
    # Alert Configuration
    ALERT_ENABLED: bool = True
    ALERT_THRESHOLD: float = 0.05  # 5% price change
    
    # System Configuration
    GRACEFUL_SHUTDOWN_TIMEOUT: int = 30
    HEALTH_CHECK_INTERVAL: int = 60
    
    # Signal Generation Settings - CONFIGURACIÓN MEJORADA PARA MÁS SEÑALES
    MIN_CONFIDENCE: float = 0.65  # Minimum confidence threshold for signals (65%) - BALANCEADO
    RISK_REWARD_MIN: float = 2.5  # Minimum risk/reward ratio - AUMENTADO PARA CALIDAD
    MAX_SIGNALS_PER_HOUR: int = 20  # Maximum signals per hour per symbol - LIBRE PARA MÁS OPORTUNIDADES

    def __init__(self):
        """Initialize settings with environment variables"""
        # Load from environment variables
        for key, value in os.environ.items():
            if hasattr(self, key):
                # Convert to appropriate type
                attr_type = type(getattr(self, key))
                if attr_type == bool:
                    setattr(self, key, value.lower() in ('true', '1', 'yes'))
                elif attr_type == int:
                    setattr(self, key, int(value))
                elif attr_type == float:
                    setattr(self, key, float(value))
                elif attr_type == list:
                    setattr(self, key, value.split(','))
                else:
                    setattr(self, key, value)
        
        logger.info("⚙️ Settings initialized")
    
    def get_primary_source(self) -> str:
        """Get primary data source name"""
        return self.DATA_SOURCE
    
    def validate_coinbase_config(self) -> bool:
        """Validate Coinbase configuration"""
        if self.DATA_SOURCE != "coinbase":
            return True  # Skip validation if not using Coinbase
            
        required_fields = [
            self.COINBASE_API_KEY,
            self.COINBASE_API_SECRET,
            self.COINBASE_PASSPHRASE
        ]
        return all(field.strip() for field in required_fields)
    
    def validate_coingecko_config(self) -> bool:
        """Validate CoinGecko configuration"""
        # CoinGecko free API doesn't require API key
        return True
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration"""
        return {
            "url": self.DATABASE_URL,
            "echo": self.DATABASE_ECHO
        }
    
    def get_coinbase_config(self) -> Dict[str, Any]:
        """Get Coinbase configuration"""
        return {
            "api_key": self.COINBASE_API_KEY,
            "api_secret": self.COINBASE_API_SECRET,
            "passphrase": self.COINBASE_PASSPHRASE,
            "sandbox": self.COINBASE_SANDBOX
        }
    
    def get_coingecko_config(self) -> Dict[str, Any]:
        """Get CoinGecko configuration"""
        return {
            "api_key": self.COINGECKO_API_KEY,
            "base_url": self.COINGECKO_BASE_URL,
            "symbols": self.SYMBOLS
        }
    
    def get_binance_config(self) -> Dict[str, Any]:
        """Get Binance configuration"""
        return {
            "api_key": self.BINANCE_API_KEY,
            "base_url": self.BINANCE_BASE_URL,
            "symbols": self.SYMBOLS
        }
    
    def get_coincap_config(self) -> Dict[str, Any]:
        """Get CoinCap configuration"""
        return {
            "base_url": self.COINCAP_BASE_URL,
            "symbols": self.SYMBOLS
        }
    
    def get_cryptocompare_config(self) -> Dict[str, Any]:
        """Get CryptoCompare configuration"""
        return {
            "api_key": self.CRYPTOCOMPARE_API_KEY,
            "base_url": self.CRYPTOCOMPARE_BASE_URL,
            "symbols": self.SYMBOLS
        }
    
    def get_data_source_config(self) -> Dict[str, Any]:
        """Get configuration for the selected data source"""
        if self.DATA_SOURCE == "coingecko":
            return self.get_coingecko_config()
        else:
            return self.get_coinbase_config()

# Create global settings instance
settings = Settings()