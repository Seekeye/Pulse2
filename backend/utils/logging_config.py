"""
ChainPulse Logging Configuration
Comprehensive logging setup with file rotation and formatting
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_level: str = "INFO", log_file: str = "chainpulse.log", 
                 max_size: int = 10, backup_count: int = 5):
    """
    Configure comprehensive logging system for ChainPulse
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file name
        max_size: Maximum log file size in MB
        backup_count: Number of backup files to keep
    """
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Custom formatter with colors for console
    class ColoredFormatter(logging.Formatter):
        """Colored formatter for console output"""
        
        COLORS = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        RESET = '\033[0m'
        
        def format(self, record):
            if record.levelname in self.COLORS:
                record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            return super().format(record)
    
    # Formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)-20s | %(levelname)-8s | %(funcName)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / log_file,
        maxBytes=max_size * 1024 * 1024,  # Convert MB to bytes
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setFormatter(detailed_formatter)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / "errors.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setFormatter(detailed_formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configure third-party loggers
    logging.getLogger("ccxt").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("telegram").setLevel(logging.INFO)
    
    # Log startup message
    startup_logger = logging.getLogger("chainpulse.startup")
    startup_logger.info("=" * 60)
    startup_logger.info("🚀 ChainPulse Logging System Initialized")
    startup_logger.info(f"📝 Log Level: {log_level}")
    startup_logger.info(f"📁 Log Directory: {log_dir.absolute()}")
    startup_logger.info(f"📄 Main Log: {log_file}")
    startup_logger.info(f"🔄 Max Size: {max_size}MB, Backups: {backup_count}")
    startup_logger.info("=" * 60)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

# Module-level logger
logger = get_logger(__name__)