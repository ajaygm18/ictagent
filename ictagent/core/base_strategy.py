"""Base strategy class and core data structures for ICT trading framework."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, time
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pandas as pd
import numpy as np


class SignalType(Enum):
    """Trade signal types."""
    BUY = "BUY"
    SELL = "SELL"
    CLOSE_LONG = "CLOSE_LONG"
    CLOSE_SHORT = "CLOSE_SHORT"
    NONE = "NONE"


class TradeStatus(Enum):
    """Trade execution status."""
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    STOPPED = "STOPPED"
    TARGET_HIT = "TARGET_HIT"


@dataclass
class Signal:
    """Trading signal with entry/exit conditions."""
    timestamp: datetime
    signal_type: SignalType
    price: float
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = 1.0
    reason: str = ""
    risk_amount: Optional[float] = None
    position_size: Optional[float] = None


@dataclass
class Trade:
    """Completed trade record."""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    position_size: float
    side: str  # 'long' or 'short'
    pnl: float
    pnl_pct: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    exit_reason: str
    strategy: str
    symbol: str
    risk_reward: Optional[float] = None
    mae: Optional[float] = None  # Maximum Adverse Excursion
    mfe: Optional[float] = None  # Maximum Favorable Excursion


@dataclass
class RiskConfig:
    """Risk management configuration."""
    risk_per_trade: float = 0.01  # 1% of equity per trade
    max_positions: int = 5
    max_daily_loss: float = 0.05  # 5% max daily loss
    position_sizing_method: str = "percent_risk"  # or 'fixed_amount', 'kelly'
    commission: float = 2.0  # Per round trip
    slippage_ticks: float = 0.5
    min_risk_reward: float = 1.0  # Minimum R:R ratio


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    initial_capital: float = 100000.0
    start_date: str = "2023-01-01"
    end_date: str = "2024-01-01"
    timeframe: str = "5m"  # 1m, 5m, 15m, 1h, 1d
    data_source: str = "yfinance"  # yfinance, csv
    symbols: List[str] = None
    benchmark: str = "SPY"
    timezone: str = "America/New_York"

    def __post_init__(self):
        if self.symbols is None:
            self.symbols = ["EURUSD", "ES"]


class StrategyBase(ABC):
    """Abstract base class for all ICT trading strategies.
    
    All strategy implementations must inherit from this class and implement
    the required abstract methods for signal generation and risk management.
    """

    def __init__(self, name: str, **kwargs):
        self.name = name
        self.parameters = kwargs
        self.signals_history: List[Signal] = []
        self.trades_history: List[Trade] = []
        self.current_position = 0  # 0 = flat, >0 = long, <0 = short
        self.last_signal_time = None
        
        # Strategy-specific parameters with defaults
        self.lookback_periods = kwargs.get('lookback_periods', 20)
        self.min_displacement_pips = kwargs.get('min_displacement_pips', 5)
        self.atr_filter_threshold = kwargs.get('atr_filter_threshold', 0.0001)
        
    @abstractmethod
    def setup(self, data: pd.DataFrame) -> None:
        """Initialize strategy with market data.
        
        Args:
            data: OHLCV DataFrame with datetime index
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame, current_bar: int) -> List[Signal]:
        """Generate trading signals based on ICT analysis.
        
        Args:
            data: OHLCV DataFrame with indicators
            current_bar: Current bar index for backtesting
            
        Returns:
            List of Signal objects
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Signal, account_value: float, 
                              risk_config: RiskConfig) -> float:
        """Calculate position size based on risk management rules.
        
        Args:
            signal: Trading signal with stop loss
            account_value: Current account equity
            risk_config: Risk management parameters
            
        Returns:
            Position size (number of shares/contracts)
        """
        pass
    
    def apply_filters(self, data: pd.DataFrame, current_bar: int) -> bool:
        """Apply strategy-specific filters (ATR, session time, etc.).
        
        Args:
            data: OHLCV DataFrame
            current_bar: Current bar index
            
        Returns:
            True if conditions pass filters
        """
        return True
    
    def validate_signal(self, signal: Signal, data: pd.DataFrame, 
                       current_bar: int) -> bool:
        """Validate signal quality and risk parameters.
        
        Args:
            signal: Generated signal
            data: Market data
            current_bar: Current bar index
            
        Returns:
            True if signal is valid
        """
        # Basic validation
        if signal.stop_loss is None:
            return False
            
        # Calculate risk-reward ratio
        if signal.signal_type in [SignalType.BUY, SignalType.SELL]:
            if signal.take_profit is not None:
                if signal.signal_type == SignalType.BUY:
                    risk = abs(signal.price - signal.stop_loss)
                    reward = abs(signal.take_profit - signal.price)
                else:
                    risk = abs(signal.stop_loss - signal.price)
                    reward = abs(signal.price - signal.take_profit)
                
                if risk > 0:
                    rr_ratio = reward / risk
                    return rr_ratio >= 1.0  # Minimum 1:1 R:R
        
        return True
    
    def get_session_filter(self, timestamp: datetime, 
                          session_start: time, session_end: time) -> bool:
        """Check if current time falls within trading session.
        
        Args:
            timestamp: Current datetime (EST)
            session_start: Session start time
            session_end: Session end time
            
        Returns:
            True if within session
        """
        current_time = timestamp.time()
        
        if session_start <= session_end:
            return session_start <= current_time <= session_end
        else:
            # Session spans midnight
            return current_time >= session_start or current_time <= session_end
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": self.name,
            "parameters": self.parameters,
            "total_signals": len(self.signals_history),
            "total_trades": len(self.trades_history),
            "current_position": self.current_position
        }
    
    def reset(self) -> None:
        """Reset strategy state for new backtest run."""
        self.signals_history.clear()
        self.trades_history.clear()
        self.current_position = 0
        self.last_signal_time = None