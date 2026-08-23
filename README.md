# Quant Bot - Self-Replicating Cryptocurrency Arbitrage Trading Bot

A sophisticated quantitative trading bot that automatically identifies and exploits cross-exchange arbitrage opportunities. On profitability, it replicates itself; on losses, it self-destructs.

## 🎯 Features

- **Cross-Exchange Arbitrage**: Real-time detection of price discrepancies across multiple exchanges
- **Self-Replication**: Automatically spawns new bot instances when profitability threshold is reached
- **Self-Destruct Mechanism**: Halts operations when losses exceed threshold
- **Real-Time P&L Monitoring**: Dashboard for tracking performance metrics
- **Risk Management**: Position sizing, stop-loss, exposure limits, and circuit breakers
- **Multiple Exchanges**: Binance, Kraken, Coinbase, FTX, and 100+ via CCXT
- **Backtesting Engine**: Historical strategy validation and optimization
- **Logging & Alerts**: Comprehensive monitoring with email/webhook notifications

## 📊 Success & Failure Criteria

### Replication (Self-Duplication)
- **Trigger**: 7 consecutive profitable days with ≥0.5% daily return
- **Action**: Spawn new bot instance with different trading pair
- **Max Instances**: 5 concurrent bots (configurable)

### Self-Destruct
- **Trigger**: 5 consecutive losing days or >15% cumulative loss in 30 days
- **Action**: Gracefully halt all trading and shut down bot
- **Notification**: Alert to user with final P&L report

### Performance Targets
- **Sharpe Ratio**: >1.5
- **Win Rate**: ≥60%
- **Max Drawdown**: <10%
- **Monthly Target**: +3-5% return

## 🏗️ Architecture

```
quant-bot/
├── bot.py                      # Main bot engine
├── strategy/
│   ├── __init__.py
│   ├── arbitrage.py            # Arbitrage detection & execution
│   ├── order_manager.py        # Order placement & tracking
│   └── risk_manager.py         # Position sizing & risk controls
├── exchanges/
│   ├── __init__.py
│   ├── exchange_manager.py     # Multi-exchange interface (CCXT)
│   └── price_fetcher.py        # Real-time price data
├── monitoring/
│   ├── __init__.py
│   ├── performance.py          # P&L tracking & metrics
│   ├── replicator.py           # Bot spawning & management
│   └── self_destruct.py        # Loss monitoring & shutdown
├── config/
│   ├── config.yaml             # Trading parameters
│   └── exchanges.yaml          # Exchange credentials
├── backtest.py                 # Historical backtesting
├── requirements.txt            # Python dependencies
├── INSTALL.md                  # Setup instructions
└── LICENSE
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- Exchange API keys (Binance, Kraken, etc.)

### Installation

```bash
git clone https://github.com/felixweed2/quant-bot.git
cd quant-bot
pip install -r requirements.txt
```

### Configuration

1. Copy and edit `config/exchanges.yaml`:
```bash
cp config/exchanges.yaml.example config/exchanges.yaml
# Add your API keys and secrets
```

2. Edit `config/config.yaml` with your trading parameters

### Running the Bot

```bash
# Backtest first
python backtest.py

# Paper trading (simulated)
python bot.py --mode paper

# Live trading (CAUTION!)
python bot.py --mode live
```

## 📈 Performance Monitoring

Access the live dashboard:
```
http://localhost:5000
```

Monitor:
- Real-time P&L
- Daily returns
- Drawdown metrics
- Active positions
- Replication status
- Self-destruct triggers

## ⚙️ Configuration

### Key Parameters (config/config.yaml)

```yaml
trading:
  min_profit_threshold: 0.005      # Minimum 0.5% profit
  profitable_days_trigger: 7       # Days until replication
  losing_days_trigger: 5           # Days until self-destruct
  max_loss_30d: 0.15               # 15% max loss in 30 days
  max_position_size: 1000          # Per trade in USD
  max_concurrent_bots: 5           # Max replicants

risk:
  stop_loss_pct: 0.02              # 2% stop loss
  take_profit_pct: 0.01            # 1% take profit
  max_exposure: 0.3                # 30% of capital

exchanges:
  - name: binance
    enabled: true
  - name: kraken
    enabled: true
  - name: coinbase
    enabled: true
```

## 🔄 Bot Lifecycle

```
START
  ↓
Initialize → Fetch Prices → Detect Arbitrage → Execute Trades
  ↓
Track P&L Daily
  ↓
┌─────────────────────────────────────┐
│ Check Profitability (7 days)        │
│ Check Losses (5 days or 15% loss)   │
└────���────────────────────────────────┘
  ↓
PROFITABLE? → YES → REPLICATE (spawn new bot)
  ↓ NO
LOSING? → YES → SELF-DESTRUCT (halt operations)
  ↓ NO
CONTINUE → (loop daily)
```

## 🔐 Security

- API keys stored in encrypted `.env` files (never in code)
- Rate limiting to prevent exchange blocks
- Order validation before execution
- Circuit breakers for extreme market conditions
- Audit logs of all trades

## 📊 Backtesting

Test strategy on historical data:

```bash
python backtest.py --start 2023-01-01 --end 2024-01-01 --pairs BTC/USDT,ETH/USDT
```

Outputs:
- Win rate
- Sharpe ratio
- Max drawdown
- Total return
- Trade statistics

## 🚨 Risk Warnings

⚠️ **This bot trades real money on live exchanges**
- Start with paper trading first
- Use small position sizes initially
- Monitor daily for the first week
- Never leave bot unattended for extended periods
- Exchanges can have outages, API issues, or market gaps
- Regulatory requirements vary by jurisdiction

## 📝 Logging

All activities logged to `logs/bot.log`:
- Trade executions
- P&L changes
- Replication events
- Self-destruct triggers
- Errors and warnings

## 🤝 Contributing

Pull requests welcome! Areas for improvement:
- Additional arbitrage strategies
- Machine learning price prediction
- More exchange integrations
- Performance optimizations

## 📄 License

MIT License - see LICENSE file

## 📞 Support

Issues? Check:
1. `logs/bot.log` for error details
2. Configuration in `config/config.yaml`
3. Exchange API rate limits
4. Network connectivity

---

**Disclaimer**: This bot is for educational purposes. Trading cryptocurrencies involves risk. Past performance does not guarantee future results. Always conduct your own research and consult a financial advisor.