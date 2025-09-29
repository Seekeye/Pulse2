#!/usr/bin/env python3
"""
Query Signals Script - Consultar señales guardadas en la base de datos
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from data.database_manager import DatabaseManager
from config.settings import settings

async def main():
    """ Main function to query signals """
    print("🔍 ChainPulse - Signal Query Tool")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager(settings.DATABASE_URL)
    if not await db_manager.initialize():
        print("❌ Failed to initialize database")
        return
    
    try:
        # Get recent signals
        print("\n📊 Recent Signals:")
        print("-" * 30)
        recent_signals = await db_manager.get_recent_signals(limit=10)
        
        if not recent_signals:
            print("No signals found in database")
        else:
            for signal in recent_signals:
                print(f"• {signal['symbol']} {signal['direction']} - {signal['confidence']:.1f}% - {signal['timestamp']}")
        
        # Get signal statistics
        print("\n📈 Signal Statistics:")
        print("-" * 30)
        stats = await db_manager.get_signal_stats()
        
        if stats:
            print(f"Total Signals: {stats.get('total_signals', 0)}")
            print(f"Buy Signals: {stats.get('buy_signals', 0)}")
            print(f"Sell Signals: {stats.get('sell_signals', 0)}")
            print(f"Sent to Telegram: {stats.get('sent_to_telegram', 0)}")
            
            print("\nSignals by Symbol:")
            for symbol, count in stats.get('symbol_stats', {}).items():
                print(f"  • {symbol}: {count}")
        
        # Get detailed signal info
        if recent_signals:
            print(f"\n🔍 Detailed Info for Latest Signal:")
            print("-" * 40)
            latest = recent_signals[0]
            print(f"Signal ID: {latest['signal_id']}")
            print(f"Symbol: {latest['symbol']}")
            print(f"Direction: {latest['direction']}")
            print(f"Confidence: {latest['confidence']:.1f}%")
            print(f"Status: {latest['status']}")
            print(f"Sent to Telegram: {latest['is_sent_to_telegram']}")
            print(f"Timestamp: {latest['timestamp']}")
    
    except Exception as e:
        print(f"❌ Error querying signals: {e}")
    
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
