""" Database Manager for ChainPulse """
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import Base, SignalRecord, MarketDataRecord, SystemStatsRecord, TrackingEventRecord
from signals.signal import Signal

logger = logging.getLogger(__name__)

class DatabaseManager:
    """ Database manager for ChainPulse """
    
    def __init__(self, database_url: str = "sqlite:///chainpulse.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.is_initialized = False
        
        logger.info(f"DatabaseManager created with URL: {database_url}")
    
    async def initialize(self) -> bool:
        """ Initialize database connection and create tables """
        try:
            logger.info("Initializing database...")
            
            # Create engine
            self.engine = create_engine(
                self.database_url,
                echo=False,  # Set to True for SQL debugging
                pool_pre_ping=True
            )
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            
            self.is_initialized = True
            logger.info("✅ Database initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database: {e}")
            return False
    
    def get_session(self) -> Session:
        """ Get database session """
        if not self.is_initialized:
            raise Exception("Database not initialized")
        return self.SessionLocal()
    
    async def save_signal(self, signal: Signal) -> bool:
        """ Save signal to database """
        try:
            if not self.is_initialized:
                logger.warning("Database not initialized, skipping signal save")
                return False
            
            session = self.get_session()
            
            # Check if signal already exists
            existing = session.query(SignalRecord).filter(
                SignalRecord.signal_id == signal.signal_id
            ).first()
            
            if existing:
                logger.debug(f"Signal {signal.signal_id} already exists in database")
                session.close()
                return True
            
            # Create new signal record
            signal_record = SignalRecord(
                signal_id=signal.signal_id,
                symbol=signal.symbol,
                direction=signal.direction.value,
                timestamp=signal.timestamp,
                entry_price=signal.entry_price,
                current_price=signal.current_price,
                tp1=signal.tp1,
                tp2=signal.tp2,
                tp3=signal.tp3,
                stop_loss=signal.stop_loss,
                confidence=signal.confidence,
                risk_reward_ratio=signal.risk_reward_ratio,
                market_context=signal.market_context.value,
                contributing_indicators=signal.contributing_indicators,
                indicator_scores=signal.indicator_scores,
                strategy=signal.strategy,
                timeframe=signal.timeframe,
                expected_duration=signal.expected_duration,
                reasoning=signal.reasoning,
                status=signal.status.value
            )
            
            session.add(signal_record)
            session.commit()
            session.close()
            
            logger.info(f"✅ Signal {signal.signal_id} saved to database")
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"❌ Database error saving signal: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
        except Exception as e:
            logger.error(f"❌ Error saving signal: {e}")
            return False
    
    async def mark_signal_sent_to_telegram(self, signal_id: str) -> bool:
        """ Mark signal as sent to Telegram """
        try:
            session = self.get_session()
            
            signal = session.query(SignalRecord).filter(
                SignalRecord.signal_id == signal_id
            ).first()
            
            if signal:
                signal.is_sent_to_telegram = True
                signal.telegram_sent_at = datetime.utcnow()
                session.commit()
                logger.debug(f"Signal {signal_id} marked as sent to Telegram")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking signal as sent: {e}")
            return False
    
    async def get_recent_signals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """ Get recent signals from database """
        try:
            session = self.get_session()
            
            signals = session.query(SignalRecord).order_by(
                SignalRecord.timestamp.desc()
            ).limit(limit).all()
            
            result = []
            for signal in signals:
                result.append({
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'timestamp': signal.timestamp.isoformat(),
                    'entry_price': signal.entry_price,
                    'confidence': signal.confidence,
                    'status': signal.status,
                    'is_sent_to_telegram': signal.is_sent_to_telegram
                })
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting recent signals: {e}")
            return []
    
    async def get_signal_stats(self) -> Dict[str, Any]:
        """ Get signal statistics """
        try:
            session = self.get_session()
            
            total_signals = session.query(SignalRecord).count()
            buy_signals = session.query(SignalRecord).filter(
                SignalRecord.direction == 'BUY'
            ).count()
            sell_signals = session.query(SignalRecord).filter(
                SignalRecord.direction == 'SELL'
            ).count()
            sent_to_telegram = session.query(SignalRecord).filter(
                SignalRecord.is_sent_to_telegram == True
            ).count()
            
            # Get signals by symbol
            symbol_stats = {}
            symbols = session.query(SignalRecord.symbol).distinct().all()
            for (symbol,) in symbols:
                count = session.query(SignalRecord).filter(
                    SignalRecord.symbol == symbol
                ).count()
                symbol_stats[symbol] = count
            
            session.close()
            
            return {
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'sent_to_telegram': sent_to_telegram,
                'symbol_stats': symbol_stats
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting signal stats: {e}")
            return {}
    
    async def save_market_data(self, symbol: str, price: float, volume: float = None, 
                             market_cap: float = None, change_24h: float = None) -> bool:
        """ Save market data to database """
        try:
            session = self.get_session()
            
            market_record = MarketDataRecord(
                symbol=symbol,
                price=price,
                volume=volume,
                market_cap=market_cap,
                change_24h=change_24h
            )
            
            session.add(market_record)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving market data: {e}")
            return False
    
    async def save_system_stats(self, stats: Dict[str, Any]) -> bool:
        """ Save system statistics """
        try:
            session = self.get_session()
            
            stats_record = SystemStatsRecord(
                total_signals_generated=stats.get('total_signals', 0),
                signals_sent_to_telegram=stats.get('signals_sent', 0),
                total_analysis_cycles=stats.get('total_analysis', 0),
                symbols_monitored=stats.get('symbols_monitored', 0),
                system_uptime_seconds=stats.get('uptime_seconds', 0),
                errors_count=stats.get('errors', 0)
            )
            
            session.add(stats_record)
            session.commit()
            session.close()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving system stats: {e}")
            return False
    
    async def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """ Clean up old data """
        try:
            session = self.get_session()
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Clean old market data
            old_market_data = session.query(MarketDataRecord).filter(
                MarketDataRecord.timestamp < cutoff_date
            ).delete()
            
            # Clean old system stats
            old_stats = session.query(SystemStatsRecord).filter(
                SystemStatsRecord.timestamp < cutoff_date
            ).delete()
            
            session.commit()
            session.close()
            
            logger.info(f"Cleaned up {old_market_data} old market data records and {old_stats} old stats records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up old data: {e}")
            return False
    
    async def save_tracking_event(self, event) -> bool:
        """ Save tracking event to database """
        try:
            session = self.get_session()
            
            event_record = TrackingEventRecord(
                signal_id=event.signal_id,
                symbol=event.symbol,
                event_type=event.event.value,
                current_price=event.current_price,
                target_price=event.target_price,
                profit_loss_pct=event.profit_loss_pct,
                message=event.message,
                timestamp=event.timestamp
            )
            
            session.add(event_record)
            session.commit()
            session.close()
            
            logger.debug(f"✅ Tracking event saved: {event.event.value} for {event.symbol}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving tracking event: {e}")
            return False
    
    async def mark_signal_closed(self, signal_id: str, reason: str) -> bool:
        """ Mark signal as closed in database """
        try:
            session = self.get_session()
            
            signal = session.query(SignalRecord).filter(
                SignalRecord.signal_id == signal_id
            ).first()
            
            if signal:
                signal.status = "CLOSED"
                signal.closed_at = datetime.utcnow()
                session.commit()
                logger.debug(f"Signal {signal_id} marked as closed: {reason}")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking signal as closed: {e}")
            return False
    
    async def update_signal_hits(self, signal_id: str, tp1_hit: bool = None, tp2_hit: bool = None, 
                                tp3_hit: bool = None, stop_loss_hit: bool = None, 
                                current_price: float = None) -> bool:
        """ Update signal hits in database """
        try:
            session = self.get_session()
            
            signal = session.query(SignalRecord).filter(
                SignalRecord.signal_id == signal_id
            ).first()
            
            if signal:
                if tp1_hit is not None:
                    signal.tp1_hit = tp1_hit
                if tp2_hit is not None:
                    signal.tp2_hit = tp2_hit
                if tp3_hit is not None:
                    signal.tp3_hit = tp3_hit
                if stop_loss_hit is not None:
                    signal.stop_loss_hit = stop_loss_hit
                if current_price is not None:
                    signal.current_price = current_price
                
                # Update status based on hits
                if tp3_hit or stop_loss_hit:
                    signal.status = "CLOSED"
                    signal.closed_at = datetime.utcnow()
                elif tp2_hit:
                    signal.status = "TP2_HIT"
                elif tp1_hit:
                    signal.status = "TP1_HIT"
                
                session.commit()
                logger.debug(f"Signal {signal_id} hits updated in database")
            
            session.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating signal hits: {e}")
            return False
    
    async def get_tracking_events(self, signal_id: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """ Get tracking events """
        try:
            session = self.get_session()
            
            query = session.query(TrackingEventRecord)
            if signal_id:
                query = query.filter(TrackingEventRecord.signal_id == signal_id)
            
            events = query.order_by(TrackingEventRecord.timestamp.desc()).limit(limit).all()
            
            result = []
            for event in events:
                result.append({
                    'id': event.id,
                    'signal_id': event.signal_id,
                    'symbol': event.symbol,
                    'event_type': event.event_type,
                    'current_price': event.current_price,
                    'target_price': event.target_price,
                    'profit_loss_pct': event.profit_loss_pct,
                    'message': event.message,
                    'timestamp': event.timestamp.isoformat()
                })
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting tracking events: {e}")
            return []

    async def get_active_signals_from_db(self) -> List[Dict[str, Any]]:
        """ Get active signals from database """
        try:
            session = self.get_session()
            
            signals = session.query(SignalRecord).filter(
                SignalRecord.status == "ACTIVE"
            ).all()
            
            result = []
            for signal in signals:
                result.append({
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'entry_price': signal.entry_price,
                    'current_price': signal.current_price,
                    'confidence': signal.confidence,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'tp1': signal.tp1,
                    'tp2': signal.tp2,
                    'tp3': signal.tp3,
                    'stop_loss': signal.stop_loss,
                    'tp1_hit': signal.tp1_hit,
                    'tp2_hit': signal.tp2_hit,
                    'tp3_hit': signal.tp3_hit,
                    'stop_loss_hit': signal.stop_loss_hit,
                    'reinforced_count': getattr(signal, 'reinforced_count', 0),
                    'conflict_count': getattr(signal, 'conflict_count', 0),
                    'timestamp': signal.timestamp.isoformat()
                })
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting active signals: {e}")
            return []

    async def get_recent_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """ Get recent signals from database """
        try:
            session = self.get_session()
            
            signals = session.query(SignalRecord).order_by(
                SignalRecord.timestamp.desc()
            ).limit(limit).all()
            
            result = []
            for signal in signals:
                result.append({
                    'signal_id': signal.signal_id,
                    'symbol': signal.symbol,
                    'direction': signal.direction,
                    'entry_price': signal.entry_price,
                    'current_price': signal.current_price,
                    'confidence': signal.confidence,
                    'risk_reward_ratio': signal.risk_reward_ratio,
                    'tp1': signal.tp1,
                    'tp2': signal.tp2,
                    'tp3': signal.tp3,
                    'stop_loss': signal.stop_loss,
                    'status': signal.status,
                    'tp1_hit': signal.tp1_hit,
                    'tp2_hit': signal.tp2_hit,
                    'tp3_hit': signal.tp3_hit,
                    'stop_loss_hit': signal.stop_loss_hit,
                    'timestamp': signal.timestamp.isoformat()
                })
            
            session.close()
            return result
            
        except Exception as e:
            logger.error(f"❌ Error getting recent signals: {e}")
            return []

    async def get_system_stats(self) -> Dict[str, Any]:
        """ Get system statistics """
        try:
            session = self.get_session()
            
            # Get total signals count
            total_signals = session.query(SignalRecord).count()
            
            # Get active signals count
            active_signals = session.query(SignalRecord).filter(
                SignalRecord.status == "ACTIVE"
            ).count()
            
            # Get successful signals count
            successful_signals = session.query(SignalRecord).filter(
                SignalRecord.status.in_(["TP1_HIT", "TP2_HIT", "TP3_HIT"])
            ).count()
            
            session.close()
            
            return {
                'total_signals': total_signals,
                'active_signals': active_signals,
                'successful_signals': successful_signals
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system stats: {e}")
            return {}

    async def clear_all_signals(self):
        """ Clear all signals from database """
        try:
            session = self.get_session()
            session.query(SignalRecord).delete()
            session.commit()
            session.close()
            logger.info("✅ All signals cleared from database")
        except Exception as e:
            logger.error(f"❌ Error clearing signals: {e}")
            raise

    async def clear_all_tracking_events(self):
        """ Clear all tracking events from database """
        try:
            session = self.get_session()
            session.query(TrackingEventRecord).delete()
            session.commit()
            session.close()
            logger.info("✅ All tracking events cleared from database")
        except Exception as e:
            logger.error(f"❌ Error clearing tracking events: {e}")
            raise

    async def save_signal_from_dict(self, signal_dict):
        """ Save signal from dictionary """
        try:
            session = self.get_session()
            
            signal_record = SignalRecord(
                signal_id=signal_dict['signal_id'],
                symbol=signal_dict['symbol'],
                direction=signal_dict['direction'],
                entry_price=signal_dict['entry_price'],
                current_price=signal_dict['current_price'],
                confidence=signal_dict['confidence'],
                risk_reward_ratio=signal_dict['risk_reward_ratio'],
                tp1=signal_dict['tp1'],
                tp2=signal_dict['tp2'],
                tp3=signal_dict['tp3'],
                stop_loss=signal_dict['stop_loss'],
                tp1_hit=signal_dict['tp1_hit'],
                tp2_hit=signal_dict['tp2_hit'],
                tp3_hit=signal_dict['tp3_hit'],
                stop_loss_hit=signal_dict['stop_loss_hit'],
                status=signal_dict['status'],
                market_context=signal_dict.get('market_context', 'NEUTRAL'),
                strategy=signal_dict.get('strategy', 'intelligent_multi_indicator'),
                timeframe=signal_dict.get('timeframe', '1h'),
                expected_duration=signal_dict.get('expected_duration', 'MEDIUM'),
                reasoning=signal_dict.get('reasoning', 'Test signal'),
                timestamp=datetime.fromisoformat(signal_dict['timestamp'].replace('Z', '+00:00'))
            )
            
            session.add(signal_record)
            session.commit()
            session.close()
            
            logger.info(f"✅ Test signal saved: {signal_dict['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ Error saving test signal: {e}")
            raise

    async def close(self):
        """ Close database connection """
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"❌ Error closing database: {e}")
