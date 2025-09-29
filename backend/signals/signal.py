""" Pulse Signal Model - Intelligent Trading Signal """

import logging 
from dataclasses import dataclass, field 
from datetime import datetime 
from typing import List, Dict, Optional 
from enum import Enum 

logger = logging.getLogger(__name__)

class SignalDirection(Enum):
    """ Signal direction enumeration """
    BUY = "BUY"
    SELL = "SELL"

class SignalStatus(Enum):
    """ Signal status enumeration """
    ACTIVE = "ACTIVE"
    TP1_HIT = "TP1_HIT"
    TP2_HIT = "TP2_HIT"
    TP3_HIT = "TP3_HIT"
    SL_HIT = "SL_HIT"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

class MarketContext(Enum):
    """ Market context enumeration """
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    SIDEWAYS = "SIDEWAYS"
    VOLATILE = "VOLATILE"
    BREAKOUT = "BREAKOUT"

@dataclass
class Signal:
    """ Intelligent trading signal with dynamic TP/SL levels """

    # Core identification 
    symbol: str 
    direction: SignalDirection
    timestamp: datetime = field(default_factory=datetime.utcnow)
    signal_id: str = field(default="")

    # Price levels 
    entry_price: float = 0.0
    current_price: float = 0.0

    # Dynamic take profit levels 
    tp1: float = 0.0
    tp2: float = 0.0
    tp3: float = 0.0
    stop_loss: float = 0.0

    # Intelligence metrics 
    confidence: float = 0.0 # 0-100%
    risk_reward_ratio: float = 0.0
    market_context: MarketContext = MarketContext.SIDEWAYS

    # Analysis data 
    contributing_indicators: List[str] = field(default_factory=list)
    indicator_scores: Dict[str, float] = field(default_factory=dict)
    key_levels: List[float] = field(default_factory=list)

    # Strategy information 
    strategy: str = "default"
    timeframe: str = "1h"
    expected_duration: str = "MEDIUM" # SHORT, MEDIUM, LONG
    reasoning: str = ""

    # Status tracking 
    status: SignalStatus = SignalStatus.ACTIVE
    
    # Tracking data
    tp1_hit: bool = False
    tp2_hit: bool = False
    tp3_hit: bool = False
    stop_loss_hit: bool = False 

    def __post_init__(self):
        """ Post initialization processing """
        if not self.signal_id:
            self.signal_id = f"{self.symbol}_{self.direction.value}_{int(self.timestamp.timestamp())}"
        
        logger.debug(f"Signal created: {self.signal_id}")
    
    @property
    def is_buy(self) -> bool:
        """ Check if signal is a buy signal """
        return self.direction == SignalDirection.BUY
    
    @property
    def is_sell(self) -> bool:
        """ Check if signal is a sell signal """
        return self.direction == SignalDirection.SELL

    @property
    def potential_profit_tp1(self) -> float:
        """ Calculate potential profit percentage for TP1 """
        if self.entry_price == 0:
            return 0.0 

        if self.is_buy:
            return ((self.tp1 - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.tp1) / self.entry_price) * 100

    @property
    def potential_loss(self) -> float:
        """ Calculate potential loss percentage """
        if self.entry_price == 0:
            return 0.0

        if self.is_buy:
            return ((self.entry_price - self.stop_loss) / self.entry_price) * 100
        else:
            return ((self.stop_loss - self.entry_price) / self.entry_price) * 100

    def to_telegram_message(self) -> str:
        """ Convert signal to formatted Telegram message """
        try:
            # Direction emoji and formatting 
            direction_emoji = "🟢 📈" if self.is_buy else "🔴 📉"
            confidence_stars = "⭐" * min(5, int(self.confidence / 20))
            
            # Confidence level description
            if self.confidence >= 80:
                confidence_desc = "MUY ALTA"
            elif self.confidence >= 60:
                confidence_desc = "ALTA"
            elif self.confidence >= 40:
                confidence_desc = "MEDIA"
            else:
                confidence_desc = "BAJA"

            # Market context emoji
            context_emoji = {
                MarketContext.TRENDING_UP: "📈",
                MarketContext.TRENDING_DOWN: "📉", 
                MarketContext.SIDEWAYS: "↔️",
                MarketContext.VOLATILE: "🌊",
                MarketContext.BREAKOUT: "🚀"
            }.get(self.market_context, "📊")
            
            # Duration emoji
            duration_emoji = {
                "SHORT": "⚡",
                "MEDIUM": "⏰", 
                "LONG": "📅"
            }.get(self.expected_duration, "⏰")
            
            message = f"""
{direction_emoji} **{self.direction.value} {self.symbol}** {direction_emoji}

💰 **Precio Actual:** ${self.current_price:.4f}
🎯 **Precio de Entrada:** ${self.entry_price:.4f}

🎯 **Niveles de Take Profit:**
   • TP1: ${self.tp1:.4f} (+{self.potential_profit_tp1:.1f}%)
   • TP2: ${self.tp2:.4f} (+{((self.tp2 - self.entry_price) / self.entry_price * 100):.1f}%)
   • TP3: ${self.tp3:.4f} (+{((self.tp3 - self.entry_price) / self.entry_price * 100):.1f}%)

🛡️ **Stop Loss:** ${self.stop_loss:.4f} (-{self.potential_loss:.1f}%)

📊 **Fuerza de la Señal:**
   • Confianza: {self.confidence:.1f}% {confidence_stars} ({confidence_desc})
   • Risk/Reward: 1:{self.risk_reward_ratio:.2f}
   
{context_emoji} **Contexto del Mercado:** {self.market_context.value.replace('_', ' ').title()}
{duration_emoji} **Duración Esperada:** {self.expected_duration}

🔍 **Indicadores Clave:**"""

            # Add top contributing indicators 
            for indicator, score in list(self.indicator_scores.items())[:3]:
                message += f"\n   • {indicator}: {score:.1f}%"
                
            if self.reasoning:
                message += f"\n\n💡 **Análisis:** {self.reasoning}"

            # Add trading advice
            if self.confidence >= 70:
                message += f"\n\n✅ **Recomendación:** Señal fuerte - Considera entrada"
            elif self.confidence >= 50:
                message += f"\n\n⚠️ **Recomendación:** Señal moderada - Usa gestión de riesgo estricta"
            else:
                message += f"\n\n🔍 **Recomendación:** Señal débil - Solo para traders experimentados"

            message += f"\n\n#{self.symbol.replace('-', '')} #{self.direction.value} #Trading #Pulse"

            logger.debug(f"Telegram message formatted for {self.signal_id}")
            return message.strip()

        except Exception as e:
            logger.error(f"Error formatting Telegram message for {self.signal_id}: {e}")
            return f"{self.direction.value} {self.symbol} - Error en formato de señal"

    def to_dict(self) -> Dict:
        """ Convert signal to dictionary for API/storage """
        return {
            "signal_id": self.signal_id,
            "symbol": self.symbol,
            "direction": self.direction.value,
            "timestamp": self.timestamp.isoformat(),
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "tp1": self.tp1,
            "tp2": self.tp2,
            "tp3": self.tp3,
            "stop_loss": self.stop_loss,
            "confidence": self.confidence,
            "risk_reward_ratio": self.risk_reward_ratio,
            "market_context": self.market_context.value,
            "contributing_indicators": self.contributing_indicators,
            "indicator_scores": self.indicator_scores,
            "strategy": self.strategy,
            "timeframe": self.timeframe,
            "expected_duration": self.expected_duration,
            "reasoning": self.reasoning,
            "status": self.status.value
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Signal':
        """ Create signal from dictionary """
        signal = cls(
            symbol=data["symbol"],
            direction=SignalDirection(data["direction"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            signal_id=data.get("signal_id", ""),
            entry_price=data.get("entry_price", 0.0),
            current_price=data.get("current_price", 0.0),
            tp1=data.get("tp1", 0.0),
            tp2=data.get("tp2", 0.0),
            tp3=data.get("tp3", 0.0),
            stop_loss=data.get("stop_loss", 0.0),
            confidence=data.get("confidence", 0.0),
            risk_reward_ratio=data.get("risk_reward_ratio", 0.0),
            market_context=MarketContext(data.get("market_context", "SIDEWAYS")),
            contributing_indicators=data.get("contributing_indicators", []),
            indicator_scores=data.get("indicator_scores", {}),
            strategy=data.get("strategy", "default"),
            timeframe=data.get("timeframe", "1h"),
            expected_duration=data.get("expected_duration", "MEDIUM"),
            reasoning=data.get("reasoning", ""),
            status=SignalStatus(data.get("status", "ACTIVE")),
        )
        return signal

# Utility functions 
def create_buy_signal(symbol:str, entry_price: float, **kwargs) -> Signal:
    """ Create a buy signal with default values """
    return Signal(
        symbol=symbol,
        direction=SignalDirection.BUY,
        entry_price=entry_price,
        current_price=entry_price,
        **kwargs
    ) 

def create_sell_signal(symbol: str, entry_price: float, **kwargs) -> Signal:
    """ Create a sell signal with default values """
    return Signal(
        symbol=symbol,
        direction=SignalDirection.SELL,
        entry_price=entry_price,
        current_price=entry_price,
        **kwargs
    ) 

               