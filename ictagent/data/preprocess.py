"""Data preprocessing utilities."""

import pandas as pd
from typing import Optional


def resample_data(df: pd.DataFrame, timeframe: str, 
                 method: str = 'ohlc') -> pd.DataFrame:
    """Resample OHLCV data to different timeframe.
    
    Args:
        df: OHLCV DataFrame
        timeframe: Target timeframe ('1m', '5m', '15m', '1h', '4h', '1d')
        method: Resampling method ('ohlc' or 'mean')
        
    Returns:
        Resampled DataFrame
    """
    if method == 'ohlc':
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
    else:
        resampled = df.resample(timeframe).mean()
    
    # Remove any NaN rows
    resampled = resampled.dropna()
    
    return resampled


def add_timezone(df: pd.DataFrame, timezone: str = 'America/New_York') -> pd.DataFrame:
    """Add timezone information to DataFrame index.
    
    Args:
        df: DataFrame with datetime index
        timezone: Target timezone
        
    Returns:
        DataFrame with timezone-aware index
    """
    if df.index.tz is None:
        df.index = df.index.tz_localize(timezone)
    else:
        df.index = df.index.tz_convert(timezone)
    
    return df


def clean_data(df: pd.DataFrame, remove_gaps: bool = True) -> pd.DataFrame:
    """Clean OHLCV data by removing invalid bars and gaps.
    
    Args:
        df: OHLCV DataFrame
        remove_gaps: Whether to remove weekend gaps
        
    Returns:
        Cleaned DataFrame
    """
    # Remove rows where OHLC are all the same (potential data issues)
    valid_bars = ~((df['open'] == df['high']) & 
                   (df['high'] == df['low']) & 
                   (df['low'] == df['close']))
    
    df_clean = df[valid_bars].copy()
    
    # Remove rows with zero or negative prices
    price_cols = ['open', 'high', 'low', 'close']
    valid_prices = (df_clean[price_cols] > 0).all(axis=1)
    df_clean = df_clean[valid_prices]
    
    # Ensure high >= low
    valid_hl = df_clean['high'] >= df_clean['low']
    df_clean = df_clean[valid_hl]
    
    # Ensure OHLC relationships
    valid_ohlc = ((df_clean['open'] >= df_clean['low']) & 
                  (df_clean['open'] <= df_clean['high']) &
                  (df_clean['close'] >= df_clean['low']) & 
                  (df_clean['close'] <= df_clean['high']))
    
    df_clean = df_clean[valid_ohlc]
    
    return df_clean