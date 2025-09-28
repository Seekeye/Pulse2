""" Signal Tracking System - Monitoreo inteligente de señales """
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

from .signal import Signal, SignalDirection, SignalStatus
from data.database_manager import DatabaseManager

logger = logging.getLogger(__name__)

class TrackingEvent(Enum):
    """ Eventos de tracking de señales """
    TP1_HIT = "tp1_hit"
    TP2_HIT = "tp2_hit" 
    TP3_HIT = "tp3_hit"
    STOP_LOSS_HIT = "stop_loss_hit"
    SIGNAL_CLOSED = "signal_closed"
    SIGNAL_REINFORCED = "signal_reinforced"
    SIGNAL_CONFLICTED = "signal_conflicted"
    SIGNAL_REPLACED = "signal_replaced"

@dataclass
class TrackingResult:
    """ Resultado del tracking de una señal """
    signal_id: str
    symbol: str
    event: TrackingEvent
    current_price: float
    target_price: float
    profit_loss_pct: float
    timestamp: datetime
    message: str

class SignalTracker:
    """ Sistema inteligente de tracking de señales """
    
    def __init__(self, database_manager: DatabaseManager):
        self.db = database_manager
        self.active_signals: Dict[str, Signal] = {}  # signal_id -> Signal
        self.symbol_signals: Dict[str, List[str]] = {}  # symbol -> [signal_ids]
        self.tracking_enabled = True
        
        logger.info("SignalTracker initialized")
    
    async def add_signal(self, signal: Signal) -> bool:
        """ Añadir nueva señal al tracking """
        try:
            # Verificar si ya existe señal activa para este símbolo
            existing_signals = self.symbol_signals.get(signal.symbol, [])
            
            if existing_signals:
                # Evaluar gestión de señales múltiples
                action = await self._evaluate_multiple_signals(signal, existing_signals)
                await self._handle_multiple_signals(signal, existing_signals, action)
            else:
                # Primera señal para este símbolo
                await self._add_new_signal(signal)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding signal to tracking: {e}")
            return False
    
    async def _add_new_signal(self, signal: Signal):
        """ Añadir nueva señal sin conflictos """
        self.active_signals[signal.signal_id] = signal
        
        if signal.symbol not in self.symbol_signals:
            self.symbol_signals[signal.symbol] = []
        self.symbol_signals[signal.symbol].append(signal.signal_id)
        
        logger.info(f"✅ Signal {signal.signal_id} added to tracking for {signal.symbol}")
    
    async def _evaluate_multiple_signals(self, new_signal: Signal, existing_signal_ids: List[str]) -> str:
        """ Evaluar qué hacer con señales múltiples """
        try:
            # Obtener señales existentes
            existing_signals = [self.active_signals[sid] for sid in existing_signal_ids if sid in self.active_signals]
            
            if not existing_signals:
                return "add"
            
            # Obtener la señal más reciente
            latest_signal = max(existing_signals, key=lambda s: s.timestamp)
            
            # Misma dirección = REINFORCE
            if new_signal.direction == latest_signal.direction:
                confidence_diff = new_signal.confidence - latest_signal.confidence
                if confidence_diff > 10:  # Nueva señal significativamente más fuerte
                    return "replace"
                else:
                    return "reinforce"
            
            # Dirección opuesta = CONFLICT
            else:
                confidence_diff = new_signal.confidence - latest_signal.confidence
                if abs(confidence_diff) > 15:  # Diferencia significativa
                    return "replace" if confidence_diff > 0 else "keep_existing"
                else:
                    return "conflict"
                    
        except Exception as e:
            logger.error(f"❌ Error evaluating multiple signals: {e}")
            return "add"
    
    async def _handle_multiple_signals(self, new_signal: Signal, existing_signal_ids: List[str], action: str):
        """ Manejar señales múltiples según la acción determinada """
        try:
            if action == "add":
                await self._add_new_signal(new_signal)
                
            elif action == "replace":
                # Reemplazar señal existente
                for signal_id in existing_signal_ids:
                    await self._close_signal(signal_id, "REPLACED")
                await self._add_new_signal(new_signal)
                logger.info(f"🔄 Signal replaced for {new_signal.symbol}")
                
            elif action == "reinforce":
                # Reforzar señal existente (NO añadir como nueva)
                await self._reinforce_signal(existing_signal_ids[0], new_signal)
                logger.info(f"💪 Signal reinforced for {new_signal.symbol} - NO nueva señal añadida")
                
            elif action == "conflict":
                # Marcar como conflicto (NO añadir como nueva)
                await self._mark_conflict(existing_signal_ids[0], new_signal.signal_id)
                logger.info(f"⚠️ Signal conflict detected for {new_signal.symbol} - NO nueva señal añadida")
                
            elif action == "keep_existing":
                # Mantener señal existente, no añadir nueva
                logger.info(f"📌 Keeping existing signal for {new_signal.symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error handling multiple signals: {e}")
    
    async def _reinforce_signal(self, signal_id: str, reinforcing_signal: Signal):
        """ Reforzar una señal existente """
        try:
            if signal_id in self.active_signals:
                signal = self.active_signals[signal_id]
                # Aumentar confianza (promedio ponderado)
                old_confidence = signal.confidence
                signal.confidence = (signal.confidence + reinforcing_signal.confidence) / 2
                
                # Actualizar en la base de datos
                await self.db.update_signal_hits(
                    signal_id, 
                    confidence=signal.confidence,
                    reinforced_count=signal.reinforced_count + 1 if hasattr(signal, 'reinforced_count') else 1
                )
                
                # Crear evento de refuerzo
                event = TrackingResult(
                    signal_id=signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.SIGNAL_REINFORCED,
                    current_price=reinforcing_signal.current_price,
                    target_price=signal.entry_price,
                    profit_loss_pct=0.0,
                    timestamp=datetime.utcnow(),
                    message=f"💪 Señal reforzada - Confianza: {old_confidence:.1f}% → {signal.confidence:.1f}%"
                )
                
                await self._save_tracking_event(event)
                
        except Exception as e:
            logger.error(f"❌ Error reinforcing signal: {e}")
    
    async def _mark_conflict(self, signal_id: str, conflicting_signal_id: str):
        """ Marcar conflicto entre señales """
        try:
            if signal_id in self.active_signals:
                signal = self.active_signals[signal_id]
                
                # Actualizar contador de conflictos en la base de datos
                await self.db.update_signal_hits(
                    signal_id, 
                    conflict_count=signal.conflict_count + 1 if hasattr(signal, 'conflict_count') else 1
                )
                
                event = TrackingResult(
                    signal_id=signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.SIGNAL_CONFLICTED,
                    current_price=signal.current_price,
                    target_price=signal.entry_price,
                    profit_loss_pct=0.0,
                    timestamp=datetime.utcnow(),
                    message=f"⚠️ Conflicto detectado con señal {conflicting_signal_id}"
                )
                
                await self._save_tracking_event(event)
                
        except Exception as e:
            logger.error(f"❌ Error marking conflict: {e}")
    
    async def update_prices(self, market_data: Dict[str, float]) -> List[TrackingResult]:
        """ Actualizar precios y verificar hits """
        results = []
        
        if not self.tracking_enabled:
            return results
        
        try:
            for signal_id, signal in self.active_signals.items():
                if signal.symbol in market_data:
                    # market_data now contains direct price values
                    current_price = market_data[signal.symbol]
                    
                    # Actualizar current_price en la base de datos
                    await self.db.update_signal_hits(signal_id, current_price=current_price)
                    
                    # Verificar hits
                    hit_result = await self._check_signal_hits(signal, current_price)
                    if hit_result:
                        results.append(hit_result)
                        
                        # Si la señal se cerró, remover del tracking
                        if hit_result.event in [TrackingEvent.TP3_HIT, TrackingEvent.STOP_LOSS_HIT, TrackingEvent.SIGNAL_CLOSED]:
                            await self._close_signal(signal_id, hit_result.event.value.upper())
                            
        except Exception as e:
            logger.error(f"❌ Error updating prices: {e}")
        
        return results
    
    async def _check_signal_hits(self, signal: Signal, current_price: float) -> Optional[TrackingResult]:
        """ Verificar si la señal ha hecho hit en algún nivel """
        try:
            # Calcular porcentaje de ganancia/pérdida
            if signal.is_buy:
                profit_loss_pct = ((current_price - signal.entry_price) / signal.entry_price) * 100
            else:
                profit_loss_pct = ((signal.entry_price - current_price) / signal.entry_price) * 100
            
            # Verificar TP1
            if not signal.tp1_hit and self._check_tp_hit(signal, current_price, signal.tp1, signal.is_buy):
                signal.tp1_hit = True
                # Update database
                await self.db.update_signal_hits(signal.signal_id, tp1_hit=True, current_price=current_price)
                return TrackingResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.TP1_HIT,
                    current_price=current_price,
                    target_price=signal.tp1,
                    profit_loss_pct=profit_loss_pct,
                    timestamp=datetime.utcnow(),
                    message=f"🎯 TP1 HIT! {signal.symbol} alcanzó {signal.tp1:.4f} (+{profit_loss_pct:.1f}%)"
                )
            
            # Verificar TP2
            elif not signal.tp2_hit and self._check_tp_hit(signal, current_price, signal.tp2, signal.is_buy):
                signal.tp2_hit = True
                # Update database
                await self.db.update_signal_hits(signal.signal_id, tp2_hit=True, current_price=current_price)
                return TrackingResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.TP2_HIT,
                    current_price=current_price,
                    target_price=signal.tp2,
                    profit_loss_pct=profit_loss_pct,
                    timestamp=datetime.utcnow(),
                    message=f"🎯 TP2 HIT! {signal.symbol} alcanzó {signal.tp2:.4f} (+{profit_loss_pct:.1f}%)"
                )
            
            # Verificar TP3 (cierra la señal)
            elif not signal.tp3_hit and self._check_tp_hit(signal, current_price, signal.tp3, signal.is_buy):
                signal.tp3_hit = True
                # Update database
                await self.db.update_signal_hits(signal.signal_id, tp3_hit=True, current_price=current_price)
                return TrackingResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.TP3_HIT,
                    current_price=current_price,
                    target_price=signal.tp3,
                    profit_loss_pct=profit_loss_pct,
                    timestamp=datetime.utcnow(),
                    message=f"🎯 TP3 HIT! {signal.symbol} alcanzó {signal.tp3:.4f} (+{profit_loss_pct:.1f}%) - SEÑAL CERRADA"
                )
            
            # Verificar Stop Loss (cierra la señal)
            elif not signal.stop_loss_hit and self._check_sl_hit(signal, current_price, signal.stop_loss, signal.is_buy):
                signal.stop_loss_hit = True
                # Update database
                await self.db.update_signal_hits(signal.signal_id, stop_loss_hit=True, current_price=current_price)
                return TrackingResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.STOP_LOSS_HIT,
                    current_price=current_price,
                    target_price=signal.stop_loss,
                    profit_loss_pct=profit_loss_pct,
                    timestamp=datetime.utcnow(),
                    message=f"🛡️ STOP LOSS HIT! {signal.symbol} alcanzó {signal.stop_loss:.4f} ({profit_loss_pct:.1f}%) - SEÑAL CERRADA"
                )
            
            # Verificar timeout (cierra la señal después de 24 horas)
            elif self._check_signal_timeout(signal):
                return TrackingResult(
                    signal_id=signal.signal_id,
                    symbol=signal.symbol,
                    event=TrackingEvent.SIGNAL_CLOSED,
                    current_price=current_price,
                    target_price=current_price,
                    profit_loss_pct=profit_loss_pct,
                    timestamp=datetime.utcnow(),
                    message=f"⏰ TIMEOUT! {signal.symbol} cerrada por tiempo ({profit_loss_pct:.1f}%) - SEÑAL CERRADA"
                )
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error checking signal hits: {e}")
            return None
    
    def _check_tp_hit(self, signal: Signal, current_price: float, target_price: float, is_buy: bool) -> bool:
        """ Verificar si se alcanzó un Take Profit """
        if is_buy:
            return current_price >= target_price
        else:
            return current_price <= target_price
    
    def _check_sl_hit(self, signal: Signal, current_price: float, stop_loss: float, is_buy: bool) -> bool:
        """ Verificar si se alcanzó el Stop Loss """
        if is_buy:
            return current_price <= stop_loss
        else:
            return current_price >= stop_loss
    
    def _check_signal_timeout(self, signal: Signal) -> bool:
        """ Verificar si la señal ha expirado por tiempo (24 horas) """
        try:
            from datetime import timedelta
            current_time = datetime.utcnow()
            signal_age = current_time - signal.timestamp
            timeout_hours = 24
            
            return signal_age.total_seconds() > (timeout_hours * 3600)
        except Exception as e:
            logger.error(f"Error checking signal timeout: {e}")
            return False
    
    async def _close_signal(self, signal_id: str, reason: str):
        """ Cerrar señal y remover del tracking """
        try:
            if signal_id in self.active_signals:
                signal = self.active_signals[signal_id]
                
                # Remover de tracking activo
                del self.active_signals[signal_id]
                
                # Remover de símbolo
                if signal.symbol in self.symbol_signals:
                    self.symbol_signals[signal.symbol].remove(signal_id)
                    if not self.symbol_signals[signal.symbol]:
                        del self.symbol_signals[signal.symbol]
                
                # Actualizar en base de datos
                await self.db.mark_signal_closed(signal_id, reason)
                
                logger.info(f"✅ Signal {signal_id} closed: {reason}")
                
        except Exception as e:
            logger.error(f"❌ Error closing signal: {e}")
    
    async def _save_tracking_event(self, event: TrackingResult):
        """ Guardar evento de tracking en base de datos """
        try:
            await self.db.save_tracking_event(event)
        except Exception as e:
            logger.error(f"❌ Error saving tracking event: {e}")
    
    async def get_active_signals(self) -> Dict[str, Signal]:
        """ Obtener señales activas """
        return self.active_signals.copy()
    
    async def get_signal_status(self, symbol: str) -> Dict:
        """ Obtener estado de señales para un símbolo """
        signal_ids = self.symbol_signals.get(symbol, [])
        signals = [self.active_signals[sid] for sid in signal_ids if sid in self.active_signals]
        
        return {
            "symbol": symbol,
            "active_signals": len(signals),
            "signals": [
                {
                    "signal_id": s.signal_id,
                    "direction": s.direction.value,
                    "confidence": s.confidence,
                    "entry_price": s.entry_price,
                    "current_price": s.current_price,
                    "tp1_hit": s.tp1_hit,
                    "tp2_hit": s.tp2_hit,
                    "tp3_hit": s.tp3_hit,
                    "stop_loss_hit": s.stop_loss_hit,
                    "status": s.status.value
                }
                for s in signals
            ]
        }
    
    async def close_signal_manually(self, signal_id: str, reason: str = "MANUALLY_CLOSED") -> bool:
        """ Cerrar señal manualmente """
        try:
            if signal_id in self.active_signals:
                await self._close_signal(signal_id, reason)
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Error closing signal manually: {e}")
            return False
    
    async def cleanup_old_signals(self, max_age_hours: int = 24):
        """ Limpiar señales muy antiguas """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            signals_to_close = []
            
            for signal_id, signal in self.active_signals.items():
                if signal.timestamp < cutoff_time:
                    signals_to_close.append(signal_id)
            
            for signal_id in signals_to_close:
                await self._close_signal(signal_id, "EXPIRED")
                
            if signals_to_close:
                logger.info(f"🧹 Cleaned up {len(signals_to_close)} old signals")
                
        except Exception as e:
            logger.error(f"❌ Error cleaning up old signals: {e}")
    
    async def get_tracking_stats(self) -> Dict:
        """ Obtener estadísticas de tracking """
        try:
            total_active = len(self.active_signals)
            symbols_tracked = len(self.symbol_signals)
            
            # Contar hits
            tp1_hits = sum(1 for s in self.active_signals.values() if s.tp1_hit)
            tp2_hits = sum(1 for s in self.active_signals.values() if s.tp2_hit)
            tp3_hits = sum(1 for s in self.active_signals.values() if s.tp3_hit)
            sl_hits = sum(1 for s in self.active_signals.values() if s.stop_loss_hit)
            
            return {
                "total_active_signals": total_active,
                "symbols_tracked": symbols_tracked,
                "tp1_hits": tp1_hits,
                "tp2_hits": tp2_hits,
                "tp3_hits": tp3_hits,
                "stop_loss_hits": sl_hits,
                "tracking_enabled": self.tracking_enabled
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting tracking stats: {e}")
            return {}
