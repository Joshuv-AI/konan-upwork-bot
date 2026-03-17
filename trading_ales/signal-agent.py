#!/usr/bin/env python3
"""
SIGNAL AGENT - MACD NEG SHORT STRATEGY
Based on strategy from Yahiko: +345% ROI, 73.4% Win Rate

Entry Rules (SHORT):
- MACD histogram < 0 (bearish)
- Volume > 1.5x 20-period average volume
- Hour UTC in [6, 7, 8, 14, 17, 20]
- Direction: SHORT

Exit Rules:
- Take Profit: Entry Price - (ATR × 0.1)
- Stop Loss: Entry Price + (ATR × 0.05)
- Max Hold: 24 candles (1H timeframe)
"""

import ccxt
import json
import time
import signal
import sys
from datetime import datetime
from pathlib import Path

# ============= CONFIG =============
API_KEY = 'wPKw4vvnanxFpHAFyFp4AduWWMd8H4LWJ7a4OBJvYDU7f5ugsBX9UoqVwMdCXVUe'
SECRET = '8HOGRZG03QWHUCJApzVyXNUR6PEkU17T9LKJPFFXQ2PwTg6yVS7cXUWZ0qYmL2T0'

e = ccxt.binanceus({'apiKey': API_KEY, 'secret': SECRET, 'enableRateLimit': True, 'timeout': 30000})

# MACD Strategy Parameters (from Yahiko)
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
VOLUME_MA_PERIOD = 20
VOLUME_MULTIPLIER = 1.5

# Trading Hours (UTC)
TRADE_HOURS = [6, 7, 8, 14, 17, 20]

# ATR Parameters
ATR_PERIOD = 14
TP_ATR_MULT = 0.1  # TP = Entry - (ATR × 0.1)
SL_ATR_MULT = 0.05  # SL = Entry + (ATR × 0.05)

# Max hold in candles (24 hours for 1H timeframe)
MAX_HOLD_CANDLES = 24

# Risk Management
RISK_PER_TRADE = 0.03  # 3% max risk
MAX_POSITIONS = 3

# Pairs - From strategy (BTC, ETH, BNB, XRP, SOL, NEAR, DOT, ADA, AVAX, MATIC, LINK, UNI)
PAIRS = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
    'NEAR/USDT', 'DOT/USDT', 'ADA/USDT', 'AVAX/USDT', 'MATIC/USDT',
    'LINK/USDT', 'UNI/USDT'
]

# Timeframe
TIMEFRAME = '1h'
LIMIT = 200
SCAN_INTERVAL = 15  # 15 seconds

# File paths
SIGNAL_FILE = 'trading_ales/research_signal.json'
LOG_FILE = 'trading_ales/logs/signal_agent.log'
HEARTBEAT_FILE = 'trading_ales/signal_heartbeat.txt'

# ============= UTILITIES =============

def log(msg):
    try:
        Path('trading_ales/logs').mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, 'a') as f:
            f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {msg}\n')
        print(msg)
    except:
        pass

def write_heartbeat():
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            f.write(str(time.time()))
    except:
        pass

def get_ohlcv(sym, tf=TIMEFRAME, limit=LIMIT):
    try:
        return e.fetch_ohlcv(sym, tf, limit=limit)
    except Exception as ex:
        log(f'Error fetching {sym}: {ex}')
        return None

# ============= INDICATORS =============

def calc_ema(prices, period):
    """Calculate EMA"""
    if len(prices) < period:
        return None
    ema = []
    multiplier = 2 / (period + 1)
    ema.append(sum(prices[:period]) / period)
    for price in prices[period:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema[-1]

def calc_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD
    Returns: (macd_line, signal_line, histogram)
    """
    if len(prices) < slow:
        return 0, 0, 0
    
    # Calculate EMAs
    ema_fast = []
    ema_slow = []
    mult_fast = 2 / (fast + 1)
    mult_slow = 2 / (slow + 1)
    
    # Initialize
    ema_fast.append(sum(prices[:fast]) / fast)
    ema_slow.append(sum(prices[:slow]) / slow)
    
    for i in range(fast, len(prices)):
        ema_fast.append((prices[i] - ema_fast[-1]) * mult_fast + ema_fast[-1])
    
    for i in range(slow, len(prices)):
        ema_slow.append((prices[i] - ema_slow[-1]) * mult_slow + ema_slow[-1])
    
    # MACD Line = Fast EMA - Slow EMA
    macd_line = ema_fast[-1] - ema_slow[-1]
    
    # Signal Line = EMA of MACD Line (simplified)
    signal_line = macd_line * 0.9  # Simplified signal
    
    # Histogram = MACD Line - Signal Line
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram

def calc_macd_full(prices, fast=12, slow=26, signal=9):
    """Full MACD calculation returning all values"""
    if len(prices) < slow + signal:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'prev_histogram': 0}
    
    # Calculate MACD line for all points
    macd_values = []
    ema_fast = []
    ema_slow = []
    mult_fast = 2 / (fast + 1)
    mult_slow = 2 / (slow + 1)
    
    # Initialize EMAs
    ema_fast = [sum(prices[:fast]) / fast]
    ema_slow = [sum(prices[:slow]) / slow]
    
    # Calculate EMAs
    for i in range(fast, len(prices)):
        ema_fast.append((prices[i] - ema_fast[-1]) * mult_fast + ema_fast[-1])
    
    for i in range(slow, len(prices)):
        ema_slow.append((prices[i] - ema_slow[-1]) * mult_slow + ema_slow[-1])
    
    # MACD line
    for i in range(slow, len(prices)):
        macd_val = ema_fast[i - (slow - fast)] - ema_slow[i - slow] if i - (slow - fast) < len(ema_fast) else 0
        macd_values.append(macd_val)
    
    if len(macd_values) < signal:
        return {'macd': 0, 'signal': 0, 'histogram': 0, 'prev_histogram': 0}
    
    # Signal line (EMA of MACD)
    signal_mult = 2 / (signal + 1)
    signal_values = [macd_values[0]]
    for i in range(1, len(macd_values)):
        signal_values.append((macd_values[i] - signal_values[-1]) * signal_mult + signal_values[-1])
    
    # Current and previous histogram
    histogram = macd_values[-1] - signal_values[-1]
    prev_histogram = macd_values[-2] - signal_values[-2] if len(signal_values) > 1 else 0
    
    return {
        'macd': macd_values[-1],
        'signal': signal_values[-1],
        'histogram': histogram,
        'prev_histogram': prev_histogram
    }

def calc_volume_ma(volumes, period=20):
    """Calculate Volume Moving Average"""
    if len(volumes) < period:
        return sum(volumes) / len(volumes) if volumes else 0
    return sum(volumes[-period:]) / period

def calc_atr(ohlc_data, period=14):
    """Calculate Average True Range"""
    if len(ohlc_data) < period + 1:
        return 0
    
    tr_values = []
    for i in range(1, len(ohlc_data)):
        high = ohlc_data[i][2]
        low = ohlc_data[i][3]
        prev_close = ohlc_data[i-1][4]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        tr_values.append(tr)
    
    if len(tr_values) < period:
        return sum(tr_values) / len(tr_values) if tr_values else 0
    
    return sum(tr_values[-period:]) / period

# ============= SIGNAL GENERATION =============

def check_macd_short_entry(data, current_hour_utc):
    """
    MACD NEG SHORT Strategy Entry:
    - MACD histogram < 0 (bearish momentum)
    - Volume > 1.5x 20-period MA
    - Hour UTC in [6, 7, 8, 14, 17, 20]
    """
    if data is None or len(data) < 50:
        return False, 0, {}
    
    # Extract close prices and volumes
    closes = [c[4] for c in data]
    volumes = [c[5] for c in data]
    
    # Calculate MACD
    macd_data = calc_macd_full(closes, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    
    # Calculate Volume MA
    volume_ma = calc_volume_ma(volumes, VOLUME_MA_PERIOD)
    current_volume = volumes[-1]
    
    # Get current hour
    timestamp = data[-1][0] / 1000  # Convert to seconds
    candle_hour = datetime.utcfromtimestamp(timestamp).hour
    
    # Entry conditions
    histogram_bearish = macd_data['histogram'] < 0
    volume_confirmed = current_volume > volume_ma * VOLUME_MULTIPLIER
    hour_confirmed = candle_hour in TRADE_HOURS
    
    # Additional: Check if histogram turning more negative (momentum building)
    momentum_confirmed = macd_data['histogram'] < macd_data['prev_histogram']
    
    # Score calculation
    if histogram_bearish and volume_confirmed and hour_confirmed:
        # Calculate score based on how bearish + volume strength
        hist_strength = abs(macd_data['histogram'])
        vol_ratio = current_volume / volume_ma
        
        score = min(10, (hist_strength / 10) * vol_ratio)
        
        indicators = {
            'histogram': macd_data['histogram'],
            'prev_histogram': macd_data['prev_histogram'],
            'volume': current_volume,
            'volume_ma': volume_ma,
            'volume_ratio': vol_ratio,
            'hour': candle_hour,
            'momentum': 'strengthening' if momentum_confirmed else 'weakening'
        }
        
        return True, round(score, 1), indicators
    
    return False, 0, {}

def generate_signal(pair):
    """Generate signal for a pair using MACD SHORT strategy"""
    data = get_ohlcv(pair)
    
    if data is None or len(data) < 50:
        return None
    
    # Extract close prices
    closes = [c[4] for c in data]
    
    # Get current hour from candle
    timestamp = data[-1][0] / 1000
    current_hour_utc = datetime.utcfromtimestamp(timestamp).hour
    
    # Check for MACD SHORT entry
    entry, score, indicators = check_macd_short_entry(data, current_hour_utc)
    
    if entry:
        current_price = closes[-1]
        
        # Calculate ATR for TP/SL
        atr = calc_atr(data, ATR_PERIOD)
        
        # Calculate TP and SL
        tp = current_price - (atr * TP_ATR_MULT)  # Target: lower price
        sl = current_price + (atr * SL_ATR_MULT)   # Stop: higher price
        
        signal = {
            'pair': pair,
            'direction': 'SHORT',  # MACD strategy is SHORT only
            'entry': current_price,
            'tp': tp,
            'sl': sl,
            'target_pct': TP_ATR_MULT * 100,  # ~10% of ATR
            'stop_pct': SL_ATR_MULT * 100,     # ~5% of ATR
            'atr': atr,
            'score': score,
            'strategy': 'MACD_NEG_SHORT',
            'indicators': indicators,
            'max_hold_candles': MAX_HOLD_CANDLES,
            'timeframe': TIMEFRAME,
            'timestamp': datetime.now().isoformat()
        }
        
        log(f"🎯 SIGNAL: {pair} SHORT @ {current_price} | TP: {tp:.4f} | SL: {sl:.4f} | Score: {score}")
        
        return signal
    
    return None

# ============= MAIN LOOP =============

def scan_markets():
    """Scan all pairs for signals"""
    signals = []
    
    for pair in PAIRS:
        try:
            signal = generate_signal(pair)
            if signal:
                signals.append(signal)
                log(f"✓ {pair}: SHORT signal found")
        except Exception as e:
            log(f"Error scanning {pair}: {e}")
    
    # Save signals
    if signals:
        # Sort by score (highest first)
        signals.sort(key=lambda x: x['score'], reverse=True)
        
        with open(SIGNAL_FILE, 'w') as f:
            json.dump(signals, f, indent=2)
        
        log(f"📊 Found {len(signals)} signals (MACD SHORT Strategy)")
    else:
        log("⏰ No signals found")
    
    return signals

def main():
    log("=" * 50)
    log("SIGNAL AGENT - MACD NEG SHORT STRATEGY")
    log(f"Pairs: {len(PAIRS)}")
    log(f"Strategy: MACD({MACD_FAST},{MACD_SLOW},{MACD_SIGNAL}) SHORT")
    log(f"Volume: >{VOLUME_MULTIPLIER}x 20-period MA")
    log(f"Hours (UTC): {TRADE_HOURS}")
    log("=" * 50)
    
    while True:
        try:
            write_heartbeat()
            signals = scan_markets()
            
            # Wait before next scan
            for _ in range(SCAN_INTERVAL):
                time.sleep(1)
                
        except KeyboardInterrupt:
            log("Stopping signal agent...")
            break
        except Exception as e:
            log(f"Error: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
