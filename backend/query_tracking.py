#!/usr/bin/env python3
"""
Query Tracking Script - Consultar tracking de señales
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from data.database_manager import DatabaseManager
from config.settings import settings

async def main():
    """ Main function to query tracking """
    print("🎯 ChainPulse - Signal Tracking Query Tool")
    print("=" * 50)
    
    # Initialize database
    db_manager = DatabaseManager(settings.DATABASE_URL)
    if not await db_manager.initialize():
        print("❌ Failed to initialize database")
        return
    
    try:
        # Get active signals
        print("\n📊 Active Signals:")
        print("-" * 30)
        active_signals = await db_manager.get_active_signals_from_db()
        
        if not active_signals:
            print("No active signals found")
        else:
            for signal in active_signals:
                status = "ACTIVE"
                if signal['tp1_hit']:
                    status += " (TP1 ✅)"
                if signal['tp2_hit']:
                    status += " (TP2 ✅)"
                if signal['tp3_hit']:
                    status += " (TP3 ✅)"
                if signal['stop_loss_hit']:
                    status += " (SL ❌)"
                
                print(f"• {signal['symbol']} {signal['direction']} - {signal['confidence']:.1f}% - {status}")
                print(f"  Entry: ${signal['entry_price']:.4f} | TP1: ${signal['tp1']:.4f} | TP2: ${signal['tp2']:.4f} | TP3: ${signal['tp3']:.4f} | SL: ${signal['stop_loss']:.4f}")
        
        # Get recent tracking events
        print("\n🎯 Recent Tracking Events:")
        print("-" * 30)
        events = await db_manager.get_tracking_events(limit=10)
        
        if not events:
            print("No tracking events found")
        else:
            for event in events:
                emoji = {
                    'tp1_hit': '🎯',
                    'tp2_hit': '🎯🎯',
                    'tp3_hit': '🎯🎯🎯',
                    'stop_loss_hit': '🛡️',
                    'signal_closed': '✅',
                    'signal_reinforced': '💪',
                    'signal_conflicted': '⚠️',
                    'signal_replaced': '🔄'
                }.get(event['event_type'], '📊')
                
                print(f"{emoji} {event['symbol']} - {event['event_type'].upper()}")
                print(f"  Price: ${event['current_price']:.4f} | P&L: {event['profit_loss_pct']:+.1f}% | {event['timestamp']}")
                if event['message']:
                    print(f"  {event['message']}")
                print()
        
        # Get tracking statistics
        print("\n📈 Tracking Statistics:")
        print("-" * 30)
        
        # Count events by type
        event_counts = {}
        for event in events:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        for event_type, count in event_counts.items():
            print(f"• {event_type.upper()}: {count}")
        
        print(f"\n• Total Active Signals: {len(active_signals)}")
        print(f"• Total Events Tracked: {len(events)}")
        
        # Get detailed signal info
        if active_signals:
            print(f"\n🔍 Detailed Info for Latest Active Signal:")
            print("-" * 40)
            latest = active_signals[0]
            print(f"Signal ID: {latest['signal_id']}")
            print(f"Symbol: {latest['symbol']}")
            print(f"Direction: {latest['direction']}")
            print(f"Confidence: {latest['confidence']:.1f}%")
            print(f"Entry Price: ${latest['entry_price']:.4f}")
            print(f"Take Profits: ${latest['tp1']:.4f} | ${latest['tp2']:.4f} | ${latest['tp3']:.4f}")
            print(f"Stop Loss: ${latest['stop_loss']:.4f}")
            print(f"Status: {'TP1 Hit' if latest['tp1_hit'] else 'Active'} | {'TP2 Hit' if latest['tp2_hit'] else ''} | {'TP3 Hit' if latest['tp3_hit'] else ''} | {'SL Hit' if latest['stop_loss_hit'] else ''}")
    
    except Exception as e:
        print(f"❌ Error querying tracking: {e}")
    
    finally:
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main())
