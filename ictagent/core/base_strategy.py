"""Base strategy class and core data structures for ICT trading framework."""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np


@dataclass
class RiskConfig:
    """Risk management configuration."""
    initial_capital: float = 100000.0
    risk_per_trade: float = 0.01  # 1% of equity per trade
    commission_round_trip: float = 2.0  # $2 per round trip
    slippage_ticks: float = 0.5
    max_positions: int = 5
    max_daily_loss: float = 0.05  # 5% max daily loss


@dataclass
class InstrumentMeta:
    """Instrument metadata for position sizing and risk calculations."""
    symbol: str
    asset_class: str  # "futures" or "forex"
    tick_size: float  # minimum price increment
    point_value: float  # USD per 1.0 price point (futures)
    pip: float = 0.0001  # for forex
    pip_value_per_standard_lot: float = 10.0  # USD per pip for 100k lot


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    engine: str = "backtrader"
    timeframe: str = "5m"  # 1m, 5m, 15m, 1h, 1d
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    data_source: str = "yfinance"
    timezone: str = "America/New_York"
    htf_bias_enabled: bool = True
    plot_results: bool = False


class StrategyBase:
    """Abstract base class for all ICT trading strategies.
    
    Each strategy implements:
    - prepare(): precompute indicators and signals on DataFrame
    - generate_signals(): return DataFrame with entry/exit conditions
    
    The Backtrader engine uses these signals for order placement.
    """

    name: str = "BASE_STRATEGY"

    def __init__(self, params: Optional[Dict[str, Any]] = None):
        self.params = params or {}
        self.df: Optional[pd.DataFrame] = None
        self.meta: Optional[InstrumentMeta] = None
        self.risk: Optional[RiskConfig] = None
        self.signals: Optional[pd.DataFrame] = None
        
        # Common ICT parameters with defaults
        self.lookback_periods = self.params.get('lookback_periods', 20)
        self.min_displacement_pips = self.params.get('min_displacement_pips', 5)
        self.atr_filter_threshold = self.params.get('atr_filter_threshold', 0.0001)
        self.htf_bias_enabled = self.params.get('htf_bias_enabled', True)

    def prepare(self, df: pd.DataFrame, meta: InstrumentMeta, risk: RiskConfig):
        """Initialize strategy with market data and configuration.
        
        Args:
            df: OHLCV DataFrame with EST timezone
            meta: Instrument metadata for position sizing
            risk: Risk management configuration
        """
        self.df = df.copy()
        self.meta = meta
        self.risk = risk
        
        # Precompute indicators
        self._add_indicators()
        
        # Generate signals DataFrame
        self.signals = self.generate_signals()

    def _add_indicators(self):
        """Add common ICT indicators to DataFrame. Override in subclasses."""
        from ictagent.indicators.ict import atr, detect_fvg
        
        # Add ATR for volatility filtering
        self.df['atr'] = atr(self.df, period=14)
        
        # Add FVG detection
        fvg_data = detect_fvg(self.df)
        self.df = pd.concat([self.df, fvg_data], axis=1)

    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals DataFrame.
        
        Returns:
            DataFrame with columns:
            - long_entry: boolean mask for long entries
            - short_entry: boolean mask for short entries
            - entry_type: 'market' or 'limit'
            - entry_price: entry price (for limit orders)
            - stop_price: stop loss price
            - tp_price: take profit price
        """
        raise NotImplementedError("Strategy must implement generate_signals()")
    
    def apply_session_filter(self, session_mask: pd.Series) -> pd.Series:
        """Apply session-based filtering to signals.
        
        Args:
            session_mask: Boolean mask for valid session times
            
        Returns:
            Filtered boolean mask
        """
        return session_mask
    
    def apply_atr_filter(self, atr_threshold: float = None) -> pd.Series:
        """Filter signals based on ATR volatility.
        
        Args:
            atr_threshold: Minimum ATR value for signal validity
            
        Returns:
            Boolean mask where ATR >= threshold
        """
        if atr_threshold is None:
            atr_threshold = self.atr_filter_threshold
            
        if 'atr' not in self.df.columns:
            return pd.Series(True, index=self.df.index)
            
        return self.df['atr'] >= atr_threshold
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and parameters."""
        return {
            "name": self.name,
            "parameters": self.params,
            "total_signals": len(self.signals) if self.signals is not None else 0,
            "data_points": len(self.df) if self.df is not None else 0
        }