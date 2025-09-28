"""
Pulse API Server - FastAPI backend for Pulse frontend
Provides REAL crypto data, signals, and WebSocket updates
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
import sqlite3
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import Pulse components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core.pulse_engine import PulseEngine
from config.settings import settings

logger = logging.getLogger(__name__)

# Global variables
pulse_engine: Optional[PulseEngine] = None
websocket_connections: List[WebSocket] = []
db_path = Path(__file__).parent.parent / "data" / "pulse_data.db"

class DataStorage:
    """Handle data storage and retrieval"""
    
    def __init__(self):
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        # Ensure data directory exists
        db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume REAL,
                change_24h REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                strength INTEGER,
                indicators TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_context (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trend TEXT,
                volatility TEXT,
                sentiment TEXT,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("✅ Database initialized")
    
    def store_price(self, symbol: str, price_data: dict):
        """Store price data"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO prices (symbol, price, volume, change_24h)
            VALUES (?, ?, ?, ?)
        ''', (
            symbol,
            price_data.get('price', 0),
            price_data.get('volume', 0),
            price_data.get('change_24h', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_prices(self) -> dict:
        """Get latest prices for all symbols"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, price, volume, change_24h, timestamp
            FROM prices p1
            WHERE timestamp = (
                SELECT MAX(timestamp) 
                FROM prices p2 
                WHERE p2.symbol = p1.symbol
            )
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        prices = {}
        for row in results:
            symbol, price, volume, change_24h, timestamp = row
            prices[symbol] = {
                'price': price,
                'volume': volume,
                'change_24h': change_24h,
                'timestamp': timestamp
            }
        
        return prices
    
    def store_signal(self, signal_data: dict):
        """Store trading signal"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO signals (symbol, action, strength, indicators)
            VALUES (?, ?, ?, ?)
        ''', (
            signal_data.get('symbol', ''),
            signal_data.get('action', ''),
            signal_data.get('strength', 0),
            json.dumps(signal_data.get('indicators', {}))
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_signals(self, limit: int = 10) -> list:
        """Get latest trading signals"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT symbol, action, strength, indicators, timestamp
            FROM signals
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        signals = []
        for row in results:
            symbol, action, strength, indicators, timestamp = row
            signals.append({
                'symbol': symbol,
                'action': action,
                'strength': strength,
                'indicators': json.loads(indicators) if indicators else {},
                'timestamp': timestamp
            })
        
        return signals

# Initialize data storage
storage = DataStorage()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    global pulse_engine
    
    # Startup
    try:
        logger.info("🚀 Starting Pulse API Server...")
        
        # Initialize Pulse Engine
        pulse_engine = PulseEngine(settings)
        if await pulse_engine.initialize():
            logger.info("✅ Pulse Engine initialized successfully")
            
            # Start background task to collect REAL data
            asyncio.create_task(real_data_collection_loop())
        else:
            logger.error("❌ Failed to initialize Pulse Engine")
            
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    if pulse_engine:
        await pulse_engine.stop()
        await pulse_engine._cleanup()
    logger.info("👋 Pulse API Server shutdown completed")

# FastAPI app with lifespan
app = FastAPI(
    title="Pulse API",
    description="Real-time crypto analysis and trading signals",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.get("/")
async def root():
    """API health check"""
    return {
        "name": "Pulse API",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/prices")
async def get_prices():
    """Get current crypto prices from database"""
    try:
        prices = storage.get_latest_prices()
        return {
            "success": True,
            "data": prices,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals")
async def get_signals():
    """Get latest trading signals from database"""
    try:
        signals = storage.get_latest_signals()
        return {
            "success": True,
            "data": signals,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history/{symbol}")
async def get_price_history(symbol: str, limit: int = 100):
    """Get price history for a symbol"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT price, volume, change_24h, timestamp
            FROM prices
            WHERE symbol = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        history = []
        for row in results:
            price, volume, change_24h, timestamp = row
            history.append({
                'price': price,
                'volume': volume,
                'change_24h': change_24h,
                'timestamp': timestamp
            })
        
        return {
            "success": True,
            "symbol": symbol,
            "data": history,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await websocket.accept()
    websocket_connections.append(websocket)
    logger.info(f"🔌 WebSocket connected. Total: {len(websocket_connections)}")
    
    try:
        # Send initial data
        prices = storage.get_latest_prices()
        signals = storage.get_latest_signals(5)
        
        await websocket.send_text(json.dumps({
            "type": "initial_data",
            "prices": prices,
            "signals": signals
        }))
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)
        logger.info(f"🔌 WebSocket disconnected. Total: {len(websocket_connections)}")

async def broadcast_to_websockets(data: dict):
    """Broadcast data to all connected WebSockets"""
    if not websocket_connections:
        return
        
    disconnected = []
    for websocket in websocket_connections:
        try:
            await websocket.send_text(json.dumps(data))
        except:
            disconnected.append(websocket)
    
    # Remove disconnected websockets
    for ws in disconnected:
        websocket_connections.remove(ws)

async def real_data_collection_loop():
    """Background task to collect REAL data from Pulse Engine"""
    while True:
        try:
            if pulse_engine and pulse_engine.data_collector:
                # Get REAL data from Pulse Engine
                for symbol in settings.SYMBOLS:
                    try:
                        # Get real price data
                        price_data = await pulse_engine.data_collector.get_symbol_data(symbol)
                        if price_data:
                            # Store in database
                            storage.store_price(symbol, price_data)
                            logger.info(f"💰 Stored {symbol}: ${price_data.get('price', 0):.4f}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error collecting {symbol}: {e}")
                
                # Get latest data and broadcast
                prices = storage.get_latest_prices()
                signals = storage.get_latest_signals(5)
                
                if prices:
                    await broadcast_to_websockets({
                        "type": "update",
                        "prices": prices,
                        "signals": signals
                    })
                    logger.info("📡 Real data broadcasted to WebSocket clients")
            
            await asyncio.sleep(60)  # Update every minute
            
        except Exception as e:
            logger.error(f"❌ Error in data collection loop: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )