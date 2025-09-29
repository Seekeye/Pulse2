""" Database Models for ChainPulse """
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class SignalRecord(Base):
    """ Signal database model """
    __tablename__ = 'signals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(100), unique=True, nullable=False)
    symbol = Column(String(20), nullable=False)
    direction = Column(String(10), nullable=False)  # BUY/SELL
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Price levels
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    tp1 = Column(Float, nullable=False)
    tp2 = Column(Float, nullable=False)
    tp3 = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    
    # Signal metrics
    confidence = Column(Float, nullable=False)
    risk_reward_ratio = Column(Float, nullable=False)
    market_context = Column(String(20), nullable=False)
    
    # Analysis data
    contributing_indicators = Column(JSON)  # Store as JSON
    indicator_scores = Column(JSON)  # Store as JSON
    strategy = Column(String(50), default="intelligent_multi_indicator")
    timeframe = Column(String(10), default="1h")
    expected_duration = Column(String(10), default="MEDIUM")
    reasoning = Column(Text)
    
    # Status tracking
    status = Column(String(20), default="ACTIVE")
    is_sent_to_telegram = Column(Boolean, default=False)
    telegram_sent_at = Column(DateTime)
    
    # Performance tracking
    tp1_hit = Column(Boolean, default=False)
    tp2_hit = Column(Boolean, default=False)
    tp3_hit = Column(Boolean, default=False)
    stop_loss_hit = Column(Boolean, default=False)
    closed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<SignalRecord(signal_id='{self.signal_id}', symbol='{self.symbol}', direction='{self.direction}')>"

class MarketDataRecord(Base):
    """ Market data database model """
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    price = Column(Float, nullable=False)
    volume = Column(Float)
    market_cap = Column(Float)
    change_24h = Column(Float)
    
    def __repr__(self):
        return f"<MarketDataRecord(symbol='{self.symbol}', price={self.price}, timestamp='{self.timestamp}')>"

class TrackingEventRecord(Base):
    """ Tracking events database model """
    __tablename__ = 'tracking_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    signal_id = Column(String(100), nullable=False)
    symbol = Column(String(20), nullable=False)
    event_type = Column(String(50), nullable=False)  # tp1_hit, tp2_hit, etc.
    current_price = Column(Float, nullable=False)
    target_price = Column(Float, nullable=False)
    profit_loss_pct = Column(Float, nullable=False)
    message = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TrackingEventRecord(signal_id='{self.signal_id}', event='{self.event_type}')>"

class SystemStatsRecord(Base):
    """ System statistics database model """
    __tablename__ = 'system_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    total_signals_generated = Column(Integer, default=0)
    signals_sent_to_telegram = Column(Integer, default=0)
    total_analysis_cycles = Column(Integer, default=0)
    symbols_monitored = Column(Integer, default=0)
    system_uptime_seconds = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<SystemStatsRecord(timestamp='{self.timestamp}', signals={self.total_signals_generated}')>"
