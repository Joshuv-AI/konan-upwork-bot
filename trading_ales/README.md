# Trading Bot

Binance trading bot with MACD NEG SHORT strategy.

## Strategy: MACD NEG SHORT

Based on strategy from Yahiko: **+345% ROI, 73.4% Win Rate**

### Entry Rules (SHORT):
- MACD histogram < 0 (bearish momentum)
- Volume > 1.5x 20-period average volume
- Hour UTC in [6, 7, 8, 14, 17, 20]

### Exit Rules:
- Take Profit: Entry Price - (ATR × 0.1)
- Stop Loss: Entry Price + (ATR × 0.05)
- Max Hold: 24 candles (1H timeframe)

### Pairs:
BTC/USDT, ETH/USDT, BNB/USDT, XRP/USDT, SOL/USDT, NEAR/USDT, DOT/USDT, ADA/USDT, AVAX/USDT, MATIC/USDT, LINK/USDT, UNI/USDT

## Files

- `signal-agent.py` - Generates trading signals
- `binance-live-bot.py` - Executes trades on Binance.US

## Setup

1. Install dependencies: `pip install ccxt pandas`
2. Configure API keys in the scripts
3. Run signal agent: `python signal-agent.py`
4. Run trading bot: `python binance-live-bot.py`

## Requirements

- Python 3.8+
- ccxt
- pandas
- Binance.US account with API keys
