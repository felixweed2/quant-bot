# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Exchange API keys (Binance, Kraken, Coinbase)
- (Optional) PostgreSQL for production
- (Optional) Redis for caching

## Step 1: Clone Repository

```bash
git clone https://github.com/felixweed2/quant-bot.git
cd quant-bot
```

## Step 2: Create Virtual Environment

```bash
# Using venv
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n quant-bot python=3.10
conda activate quant-bot
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Configure Exchanges

1. Copy the example configuration:
```bash
cp config/exchanges.yaml.example config/exchanges.yaml
```

2. Edit `config/exchanges.yaml` with your API credentials:

### Getting Exchange API Keys

#### Binance
1. Go to https://www.binance.com/en/account/login
2. Navigate to API Management
3. Create new API key
4. Enable "Spot & Margin Trading"
5. Copy API Key and Secret

#### Kraken
1. Go to https://www.kraken.com/
2. Settings → API → Generate New Key
3. Query Funds + Access Funds + Query Open Orders + Query Closed Orders
4. Copy API Key and Private Key

#### Coinbase
1. Go to https://www.coinbase.com/settings/api
2. Create new API key
3. Enable relevant permissions
4. Copy Key, Secret, and Passphrase

**⚠️ SECURITY WARNING:**
- Never share API keys
- Use IP whitelisting on exchanges
- Enable 2FA on all exchange accounts
- Consider using sub-accounts for bot trading
- Keep `config/exchanges.yaml` in `.gitignore`

## Step 5: Configure Trading Parameters

Edit `config/config.yaml`:

```yaml
trading:
  profitable_days_trigger: 7        # Days until replication
  losing_days_trigger: 5             # Days until self-destruct
  min_profit_threshold: 0.005       # 0.5% daily minimum

risk:
  max_position_size_usd: 1000       # Start small!
  max_exposure_pct: 0.30            # 30% of capital
  stop_loss_pct: 0.02               # 2% stop loss
```

## Step 6: Start with Paper Trading

**Always test in paper/simulation mode first:**

```bash
# Edit config/config.yaml
# Set: bot.mode: "paper"

python bot.py
```

Monitor the dashboard at `http://localhost:5000`

## Step 7: Backtest Historical Data

```bash
python backtest.py --start 2023-01-01 --end 2024-01-01
```

Review results:
- Sharpe ratio
- Win rate
- Max drawdown
- Total return

## Step 8: Live Trading (CAUTION!)

Only proceed after:
- ✅ Paper trading for 1-2 weeks
- ✅ Backtesting shows consistent profitability
- ✅ Understanding all risk settings
- ✅ Starting with small position sizes

```bash
# Edit config/config.yaml
# Set: bot.mode: "live"

python bot.py
```

## Docker Deployment (Optional)

```bash
docker build -t quant-bot .
docker run -d \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  -p 5000:5000 \
  quant-bot
```

## Database Setup (PostgreSQL)

For production with multiple bot instances:

```bash
# Create database
createdb quant_bot
createuser quant_user

# Apply migrations
python -m alembic upgrade head
```

Update `config/config.yaml`:
```yaml
database:
  type: "postgresql"
  host: "localhost"
  name: "quant_bot"
  user: "quant_user"
```

## Redis Setup (Optional, for Caching)

```bash
# Install Redis
brew install redis  # macOS
# or
sudo apt-get install redis-server  # Linux

# Start Redis
redis-server

# Update config
cache:
  type: "redis"
  host: "localhost"
```

## Monitoring Setup

### Telegram Notifications (Optional)

1. Create bot: @BotFather on Telegram
2. Get your chat ID
3. Add to `config/exchanges.yaml`:
```yaml
notifications:
  telegram_chat_id: "123456789"
```

### Slack Notifications (Optional)

1. Create incoming webhook: https://api.slack.com/messaging/webhooks
2. Copy webhook URL
3. Add to `config/exchanges.yaml`:
```yaml
notifications:
  slack_webhook_url: "https://hooks.slack.com/..."
```

## Troubleshooting

### "No module named 'ccxt'"
```bash
pip install ccxt
```

### API Connection Errors
- Check API keys in `config/exchanges.yaml`
- Verify IP whitelisting on exchange
- Check internet connection
- Ensure API key has correct permissions

### Database Connection Failed
```bash
# Check PostgreSQL is running
psql -U quant_user -d quant_bot
```

### Memory Issues
- Reduce `max_concurrent_bots` in config
- Use SQLite instead of PostgreSQL for testing
- Close other applications

## Logs

View bot logs:
```bash
tail -f logs/bot.log
```

## Stopping the Bot

```bash
# Graceful shutdown
Ctrl+C

# Force shutdown (use only if needed)
pkill -f "python bot.py"
```

## Production Checklist

- [ ] API keys configured with IP whitelisting
- [ ] 2FA enabled on all exchange accounts
- [ ] Paper trading validation complete
- [ ] Backtesting shows positive results
- [ ] Starting capital is small (test amount)
- [ ] Monitoring alerts configured
- [ ] Logging to file configured
- [ ] Database backups scheduled
- [ ] Regular log rotation enabled
- [ ] Understand all risk parameters

## Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Restrict API key permissions** to minimum needed
4. **Enable IP whitelisting** on exchanges
5. **Use separate sub-accounts** for bot trading
6. **Regularly rotate API keys**
7. **Monitor account activity** for suspicious trades
8. **Keep dependencies updated**: `pip install --upgrade -r requirements.txt`

## Support & Issues

- Check logs: `logs/bot.log`
- Review config: `config/config.yaml`
- Test connectivity: `python -c "import ccxt; print(ccxt.binance())"`
- GitHub Issues: Create detailed issue with logs

---

Ready to trade! Start with paper mode and work your way up. 🚀
