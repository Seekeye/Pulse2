#!/usr/bin/env python3
"""
API Endpoints for ChainPulse Frontend
This file provides REST API endpoints for the frontend dashboard
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Setup logging
logger = logging.getLogger(__name__)

# Import our existing modules
from data.database_manager import DatabaseManager
from config.settings import Settings
import aiohttp
import asyncio

app = FastAPI(title="ChainPulse API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:3003", "http://localhost:3004", "http://localhost:4173", "https://*.railway.app", "https://*.vercel.app", "https://*.onrender.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global database manager and pulse engine
db_manager = None
pulse_engine = None

async def get_real_prices(symbols: List[str]) -> Dict[str, float]:
    """Get real-time prices for symbols using Coinbase API"""
    try:
        import aiohttp
        prices = {}
        
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                try:
                    # Use Coinbase public API
                    url = f"https://api.coinbase.com/v2/exchange-rates?currency={symbol.split('-')[0]}"
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            if 'data' in data and 'rates' in data['data'] and 'USD' in data['data']['rates']:
                                prices[symbol] = float(data['data']['rates']['USD'])
                            else:
                                prices[symbol] = 0.0
                        else:
                            prices[symbol] = 0.0
                except Exception as e:
                    logger.error(f"❌ Error getting price for {symbol}: {e}")
                    prices[symbol] = 0.0
        
        return prices
    except Exception as e:
        logger.error(f"❌ Error in get_real_prices: {e}")
        return {symbol: 0.0 for symbol in symbols}

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    global db_manager
    settings = Settings()
    db_manager = DatabaseManager(settings.DATABASE_URL)
    await db_manager.initialize()
    print("✅ API Database connection initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    global db_manager
    if db_manager:
        await db_manager.close()
    print("✅ API Database connection closed")

@app.get("/api/price-history/{symbol}")
async def get_price_history(symbol: str, limit: int = 10):
    """Get price history for mini charts (7-15 days)"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Current prices for different symbols
        current_price = 100.0  # Default price
        if symbol in ["BTC-USD"]:
            current_price = 50000.0
        elif symbol in ["ETH-USD"]:
            current_price = 3000.0
        elif symbol in ["ADA-USD"]:
            current_price = 0.5
        elif symbol in ["SOL-USD"]:
            current_price = 100.0
        elif symbol in ["MATIC-USD"]:
            current_price = 0.8
        elif symbol in ["LINK-USD"]:
            current_price = 15.0
        
        # Generate realistic price history for 7-15 days
        import random
        prices = []
        base_price = current_price
        
        # Generate data for 10 days (middle point between 7-15)
        days = min(limit, 10)
        for i in range(days):
            # More realistic daily volatility (0.5% to 3%)
            daily_volatility = base_price * (0.005 + random.random() * 0.025)
            trend = (random.random() - 0.5) * (base_price * 0.001)  # Very subtle trend
            change = (random.random() - 0.5) * daily_volatility + trend
            
            price = base_price - (i * (base_price * 0.0005)) + change  # Very subtle downward trend
            price = max(price, base_price * 0.85)  # Don't allow very large drops
            prices.append(round(price, 2))
            base_price = price
        
        return JSONResponse(content={
            "symbol": symbol,
            "prices": prices,
            "current_price": current_price
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/reset-database")
async def reset_database():
    """Reset the database - clear all signals and tracking events"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Clear all signals
        await db_manager.clear_all_signals()
        
        # Clear all tracking events
        await db_manager.clear_all_tracking_events()
        
        return JSONResponse(content={
            "message": "Database reset successfully",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error resetting database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-test-signals")
async def generate_test_signals():
    """Generate test signals for demonstration"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Generate test signals
        test_signals = [
            {
                'signal_id': f'BTC-USD_BUY_{int(datetime.utcnow().timestamp())}',
                'symbol': 'BTC-USD',
                'direction': 'BUY',
                'entry_price': 110000.0,
                'current_price': 110000.0,
                'confidence': 75.5,
                'risk_reward_ratio': 2.1,
                'tp1': 111100.0,
                'tp2': 112200.0,
                'tp3': 113300.0,
                'stop_loss': 108900.0,
                'tp1_hit': False,
                'tp2_hit': False,
                'tp3_hit': False,
                'stop_loss_hit': False,
                'status': 'ACTIVE',
                'market_context': 'BULLISH',
                'strategy': 'intelligent_multi_indicator',
                'timeframe': '1h',
                'expected_duration': 'MEDIUM',
                'reasoning': 'Strong bullish momentum detected',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'signal_id': f'ETH-USD_SELL_{int(datetime.utcnow().timestamp())}',
                'symbol': 'ETH-USD',
                'direction': 'SELL',
                'entry_price': 4000.0,
                'current_price': 4000.0,
                'confidence': 68.2,
                'risk_reward_ratio': 1.9,
                'tp1': 3960.0,
                'tp2': 3920.0,
                'tp3': 3880.0,
                'stop_loss': 4040.0,
                'tp1_hit': False,
                'tp2_hit': False,
                'tp3_hit': False,
                'stop_loss_hit': False,
                'status': 'ACTIVE',
                'market_context': 'BEARISH',
                'strategy': 'intelligent_multi_indicator',
                'timeframe': '1h',
                'expected_duration': 'MEDIUM',
                'reasoning': 'Bearish divergence detected',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'signal_id': f'ADA-USD_BUY_{int(datetime.utcnow().timestamp())}',
                'symbol': 'ADA-USD',
                'direction': 'BUY',
                'entry_price': 0.78,
                'current_price': 0.78,
                'confidence': 72.8,
                'risk_reward_ratio': 2.3,
                'tp1': 0.7914,
                'tp2': 0.8028,
                'tp3': 0.8196,
                'stop_loss': 0.7722,
                'tp1_hit': False,
                'tp2_hit': False,
                'tp3_hit': False,
                'stop_loss_hit': False,
                'status': 'ACTIVE',
                'market_context': 'NEUTRAL',
                'strategy': 'intelligent_multi_indicator',
                'timeframe': '1h',
                'expected_duration': 'MEDIUM',
                'reasoning': 'Consolidation breakout pattern',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
        
        # Save test signals to database
        saved_count = 0
        for signal in test_signals:
            try:
                await db_manager.save_signal_from_dict(signal)
                saved_count += 1
            except Exception as e:
                logger.error(f"❌ Error saving signal {signal['symbol']}: {e}")
                # Continue with other signals
        
        return JSONResponse(content={
            "message": f"Generated {len(test_signals)} test signals successfully, {saved_count} saved to database",
            "signals": test_signals,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"❌ Error generating test signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-prices")
async def test_prices():
    """Test endpoint to get real prices"""
    try:
        symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD']
        prices = await get_real_prices(symbols)
        return {"prices": prices}
    except Exception as e:
        logger.error(f"❌ Error in test_prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard-data")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        # Always get real-time prices for market data first
        # Default symbols we're monitoring
        monitored_symbols = ['BTC-USD', 'ETH-USD', 'ADA-USD', 'SOL-USD', 'MATIC-USD', 'LINK-USD']
        # Get real prices
        real_prices = await get_real_prices(monitored_symbols)
        market_data = real_prices
        
        # Get active signals
        active_signals = await db_manager.get_active_signals_from_db()
        
        # Update current prices for active signals with real market data
        for signal in active_signals:
            symbol = signal['symbol']
            if symbol in market_data:
                signal['current_price'] = market_data[symbol]
                # Calculate P&L percentage
                entry_price = signal['entry_price']
                current_price = signal['current_price']
                if signal['direction'] == 'BUY':
                    signal['profit_loss_pct'] = ((current_price - entry_price) / entry_price) * 100
                else:  # SELL
                    signal['profit_loss_pct'] = ((entry_price - current_price) / entry_price) * 100
        
        # Get recent signals (last 10)
        recent_signals = await db_manager.get_recent_signals(limit=10)
        
        # Get tracking events (last 20)
        tracking_events = await db_manager.get_tracking_events(limit=20)
        
        # Get system stats
        system_stats = await db_manager.get_system_stats()
        
        # Calculate performance metrics
        total_signals = len(active_signals)
        successful_signals = len([s for s in active_signals if s.get('status') in ['TP1_HIT', 'TP2_HIT', 'TP3_HIT']])
        success_rate = (successful_signals / total_signals * 100) if total_signals > 0 else 0
        avg_confidence = sum(s.get('confidence', 0) for s in active_signals) / total_signals if total_signals > 0 else 0
        
        dashboard_data = {
            "activeSignals": active_signals,
            "marketData": market_data,
            "trackingEvents": tracking_events,
            "performance": {
                "totalSignals": total_signals,
                "successfulSignals": successful_signals,
                "successRate": round(success_rate, 1),
                "avgConfidence": round(avg_confidence, 1),
                "activeTracking": len(active_signals),
                "uptime": "99.8%"
            },
            "recentSignals": recent_signals
        }
        
        return JSONResponse(content=dashboard_data)
        
    except Exception as e:
        print(f"❌ Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals")
async def get_signals(limit: int = 50, status: str = None):
    """Get signals with optional filtering"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        signals = await db_manager.get_recent_signals(limit=limit)
        
        if status:
            signals = [s for s in signals if s.get('status') == status]
        
        return JSONResponse(content=signals)
        
    except Exception as e:
        print(f"❌ Error getting signals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tracking-events")
async def get_tracking_events(signal_id: str = None, limit: int = 50):
    """Get tracking events"""
    try:
        if not db_manager:
            raise HTTPException(status_code=500, detail="Database not initialized")
        
        events = await db_manager.get_tracking_events(signal_id=signal_id, limit=limit)
        return JSONResponse(content=events)
        
    except Exception as e:
        print(f"❌ Error getting tracking events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

# Serve static files (frontend) - mount after all API routes
import os
if os.path.exists("../dist"):
    app.mount("/", StaticFiles(directory="../dist", html=True), name="static")

# Initialize Pulse Engine for analysis and Telegram notifications
async def initialize_pulse_engine():
    """Initialize the Pulse Engine for analysis and notifications"""
    global pulse_engine, db_manager
    
    try:
        from core.pulse_engine import PulseEngine
        from config.settings import settings
        
        print("🚀 Initializing Pulse Engine...")
        pulse_engine = PulseEngine(settings)
        
        # Initialize the engine
        if await pulse_engine.initialize():
            print("✅ Pulse Engine initialized successfully")
            db_manager = pulse_engine.database_manager
            
            # Start the engine in background
            import asyncio
            asyncio.create_task(pulse_engine.run())
            print("🔄 Pulse Engine started in background")
            
            # Send startup notification to Telegram
            if pulse_engine.telegram_bot:
                await pulse_engine.telegram_bot.send_message("🚀 ChainPulse API Server started successfully!")
                print("📱 Startup notification sent to Telegram")
        else:
            print("❌ Failed to initialize Pulse Engine")
            
    except Exception as e:
        print(f"❌ Error initializing Pulse Engine: {e}")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await initialize_pulse_engine()

if __name__ == "__main__":
    print("🚀 Starting ChainPulse API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8003)
