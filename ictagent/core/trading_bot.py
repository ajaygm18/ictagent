"""Main trading bot orchestrating strategies and backtesting."""

from typing import List, Dict, Any, Optional
import pandas as pd
from ictagent.core.base_strategy import StrategyBase, RiskConfig, BacktestConfig, InstrumentMeta
from ictagent.data.loader import load_yfinance
from ictagent.engines.backtest_backtrader import BacktraderEngine
from ictagent.metrics.performance import PerformanceAnalyzer


class ICTTradingBot:
    """Main ICT trading bot for strategy execution and backtesting."""
    
    # Predefined instrument metadata
    INSTRUMENTS = {
        'ES=F': InstrumentMeta(
            symbol='ES=F',
            asset_class='futures',
            tick_size=0.25,
            point_value=50.0
        ),
        'EURUSD=X': InstrumentMeta(
            symbol='EURUSD=X',
            asset_class='forex',
            tick_size=0.00001,
            point_value=1.0,
            pip=0.0001,
            pip_value_per_standard_lot=10.0
        ),
        'DX-Y.NYB': InstrumentMeta(
            symbol='DX-Y.NYB',
            asset_class='index',
            tick_size=0.001,
            point_value=1000.0
        )
    }
    
    def __init__(self, risk_config: Optional[RiskConfig] = None):
        self.risk_config = risk_config or RiskConfig()
        self.strategies: List[StrategyBase] = []
        self.results: Dict[str, Any] = {}
        
    def add_strategy(self, strategy: StrategyBase):
        """Add strategy to the bot."""
        self.strategies.append(strategy)
        
    def get_instrument_meta(self, symbol: str) -> InstrumentMeta:
        """Get instrument metadata for symbol."""
        if symbol in self.INSTRUMENTS:
            return self.INSTRUMENTS[symbol]
        
        # Default metadata for unknown instruments
        return InstrumentMeta(
            symbol=symbol,
            asset_class='unknown',
            tick_size=0.01,
            point_value=1.0
        )
    
    def backtest(self, symbol: str, config: BacktestConfig) -> Dict[str, Any]:
        """Run backtest for all strategies on given symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'ES=F', 'EURUSD=X')
            config: Backtest configuration
            
        Returns:
            Dictionary with backtest results
        """
        if not self.strategies:
            raise ValueError("No strategies added to bot")
        
        # Load data
        print(f"Loading data for {symbol}...")
        df = load_yfinance(symbol, config.timeframe, config.start_date, config.end_date)
        
        if df.empty:
            raise ValueError(f"No data loaded for {symbol}")
        
        print(f"Loaded {len(df)} bars from {df.index[0]} to {df.index[-1]}")
        
        # Get instrument metadata
        meta = self.get_instrument_meta(symbol)
        
        # Initialize backtest engine
        engine = BacktraderEngine()
        
        results = {}
        
        # Run backtest for each strategy
        for strategy in self.strategies:
            print(f"\nRunning backtest for {strategy.name}...")
            
            # Prepare strategy with data
            strategy.prepare(df, meta, self.risk_config)
            
            # Run backtest
            result = engine.run_backtest(strategy, df, meta, self.risk_config, config)
            
            # Analyze performance
            analyzer = PerformanceAnalyzer()
            performance = analyzer.analyze(result['trades'], self.risk_config.initial_capital)
            
            results[strategy.name] = {
                'strategy_info': strategy.get_strategy_info(),
                'backtest_result': result,
                'performance': performance
            }
            
            print(f"Completed {strategy.name}: {len(result['trades'])} trades")
        
        self.results = results
        return results
    
    def get_performance_summary(self) -> pd.DataFrame:
        """Get performance summary for all strategies."""
        if not self.results:
            return pd.DataFrame()
        
        summary_data = []
        
        for strategy_name, result in self.results.items():
            perf = result['performance']
            summary_data.append({
                'Strategy': strategy_name,
                'Total Trades': perf['total_trades'],
                'Win Rate %': round(perf['win_rate'] * 100, 2),
                'Profit Factor': round(perf['profit_factor'], 2),
                'Sharpe Ratio': round(perf['sharpe_ratio'], 2),
                'Max Drawdown %': round(perf['max_drawdown'] * 100, 2),
                'Total Return %': round(perf['total_return'] * 100, 2),
                'CAGR %': round(perf['cagr'] * 100, 2)
            })
        
        return pd.DataFrame(summary_data)
    
    def plot_results(self, strategy_name: Optional[str] = None):
        """Plot equity curves and performance metrics."""
        from ictagent.utils.plotting import plot_equity_curve, plot_drawdown
        
        if not self.results:
            print("No backtest results to plot. Run backtest first.")
            return
        
        strategies_to_plot = [strategy_name] if strategy_name else list(self.results.keys())
        
        for name in strategies_to_plot:
            if name in self.results:
                trades = self.results[name]['backtest_result']['trades']
                if trades:
                    print(f"\nPlotting results for {name}...")
                    plot_equity_curve(trades, self.risk_config.initial_capital, name)
                    plot_drawdown(trades, self.risk_config.initial_capital, name)
                else:
                    print(f"No trades to plot for {name}")
            else:
                print(f"Strategy {name} not found in results")