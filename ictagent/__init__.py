"""ICT Agent - Algorithmic Trading Framework

A comprehensive Python-based algorithmic trading framework implementing
Inner Circle Trader (ICT) strategies with modular architecture.
"""

__version__ = "1.0.0"
__author__ = "ajaygm18"

from .core.trading_bot import ICTTradingBot
from .core.base_strategy import StrategyBase, Signal, Trade, RiskConfig, BacktestConfig

__all__ = [
    "ICTTradingBot",
    "StrategyBase", 
    "Signal",
    "Trade",
    "RiskConfig",
    "BacktestConfig"
]