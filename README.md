# ICT Agent - Algorithmic Trading Framework

A comprehensive Python-based algorithmic trading framework implementing Inner Circle Trader (ICT) strategies with modular architecture, backtesting capabilities, and performance analytics.

## Features

- **15 ICT Strategy Modules**: Complete implementation of key ICT concepts
- **Modular Architecture**: Each strategy is independently coded and configurable
- **Risk Management**: Built-in stop-loss, take-profit, and position sizing
- **Session-Based Trading**: Respects ICT session timing (London, NY, Power Hour)
- **Backtesting Engine**: Historical strategy performance analysis
- **Real-time Trading**: Live market execution capabilities
- **Performance Analytics**: Comprehensive metrics and equity curve visualization

## ICT Strategies Implemented

1. **SILVER_BULLET** - NY Killzone liquidity sweeps
2. **PRE_MARKET_BREAKOUT** - Range breakout at market open
3. **MARKET_OPEN_REVERSAL** - False breakout reversals
4. **POWER_HOUR** - Afternoon session momentum trades
5. **FVG_SNIPER** - Fair Value Gap precision entries
6. **ORDER_BLOCK** - Institutional order block retests
7. **BREAKER_BLOCK** - Failed order block reversals
8. **REJECTION_BLOCK** - Strong rejection continuations
9. **SMT_DIVERGENCE** - Smart Money Technique divergences
10. **TURTLE_SOUP** - Failed breakout reversals
11. **POWER_OF_3** - Daily manipulation patterns
12. **DAILY_BIAS_LIQUIDITY** - Higher timeframe bias alignment
13. **MORNING_SESSION** - London-NY overlap trades
14. **AFTERNOON_REVERSAL** - End-of-day reversals
15. **OPTIMAL_TRADE_ENTRY** - Fibonacci OTE zone entries

## Installation

```bash
# Clone the repository
git clone https://github.com/ajaygm18/ictagent.git
cd ictagent

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from ictagent import ICTTradingBot
from strategies.fvg_sniper import FVGSniperStrategy

# Initialize trading bot
bot = ICTTradingBot(
    data_source='yahoo',  # or 'binance', 'csv'
    initial_capital=10000,
    risk_per_trade=0.02
)

# Add strategy
bot.add_strategy(FVGSniperStrategy())

# Run backtest
results = bot.backtest(
    symbol='EURUSD',
    start_date='2023-01-01',
    end_date='2024-01-01'
)

# View performance
bot.plot_results()
print(bot.get_performance_metrics())
```

## Project Structure

```
ictagent/
├── core/
│   ├── __init__.py
│   ├── base_strategy.py      # Strategy base class
│   ├── trading_bot.py        # Main trading engine
│   ├── data_manager.py       # Data handling
│   ├── risk_manager.py       # Risk management
│   └── utils.py             # Utility functions
├── strategies/
│   ├── __init__.py
│   ├── silver_bullet.py
│   ├── fvg_sniper.py
│   ├── order_block.py
│   └── ... (all 15 strategies)
├── indicators/
│   ├── __init__.py
│   ├── ict_indicators.py     # ICT-specific indicators
│   └── market_structure.py   # Market structure analysis
├── backtesting/
│   ├── __init__.py
│   ├── backtest_engine.py
│   └── performance_metrics.py
├── data/
│   └── sample_data.csv
├── tests/
│   └── test_strategies.py
├── examples/
│   ├── basic_backtest.py
│   ├── live_trading.py
│   └── strategy_comparison.py
├── requirements.txt
├── README.md
└── main.py
```

## Configuration

Create a `.env` file for API keys and settings:

```env
# Data Provider API Keys
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret
ALPHA_VANTAGE_KEY=your_alpha_vantage_key

# Trading Settings
DEFAULT_RISK_PER_TRADE=0.02
DEFAULT_INITIAL_CAPITAL=10000
MAX_POSITIONS=5

# Session Times (EST)
LONDON_OPEN=02:00
LONDON_CLOSE=11:00
NY_OPEN=09:30
NY_CLOSE=16:00
```

## Usage Examples

### Strategy-Specific Backtesting

```python
# Test Silver Bullet strategy
from strategies.silver_bullet import SilverBulletStrategy

strategy = SilverBulletStrategy(
    killzone_start='10:00',
    killzone_end='11:00',
    min_displacement_pips=5
)

bot.add_strategy(strategy)
results = bot.backtest('GBPUSD', '2023-01-01', '2024-01-01')
```

### Multi-Strategy Portfolio

```python
# Run multiple strategies together
strategies = [
    FVGSniperStrategy(),
    OrderBlockStrategy(),
    SilverBulletStrategy()
]

for strategy in strategies:
    bot.add_strategy(strategy)
    
results = bot.backtest_portfolio(['EURUSD', 'GBPUSD', 'USDJPY'])
```

## Performance Metrics

- **Sharpe Ratio**: Risk-adjusted returns
- **Win Rate**: Percentage of profitable trades
- **Max Drawdown**: Largest peak-to-trough decline
- **Profit Factor**: Gross profit / Gross loss
- **Average Trade**: Mean profit per trade
- **Expectancy**: Expected value per trade

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-strategy`)
3. Commit changes (`git commit -am 'Add new ICT strategy'`)
4. Push to branch (`git push origin feature/new-strategy`)
5. Create Pull Request

## License

MIT License - see LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk and is not suitable for all investors. Past performance is not indicative of future results.

---

**Author**: [ajaygm18](https://github.com/ajaygm18)
**Version**: 1.0.0
**Last Updated**: September 2025