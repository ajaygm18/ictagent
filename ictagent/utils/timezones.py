"""Timezone handling utilities for EST/DST awareness."""

import pandas as pd
from typing import Union

NY_TZ = "America/New_York"


def ensure_est_timezone(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has EST timezone on its index.
    
    Args:
        df: DataFrame with datetime index
        
    Returns:
        DataFrame with EST timezone
    """
    df_copy = df.copy()
    
    if df_copy.index.tz is None:
        # No timezone info - assume UTC and convert to EST
        df_copy.index = df_copy.index.tz_localize('UTC').tz_convert(NY_TZ)
    elif df_copy.index.tz.zone != NY_TZ:
        # Different timezone - convert to EST
        df_copy.index = df_copy.index.tz_convert(NY_TZ)
    
    return df_copy


def convert_to_utc(timestamp: Union[pd.Timestamp, pd.DatetimeIndex]) -> Union[pd.Timestamp, pd.DatetimeIndex]:
    """Convert EST timestamp/index to UTC.
    
    Args:
        timestamp: EST timestamp or DatetimeIndex
        
    Returns:
        UTC timestamp or DatetimeIndex
    """
    if isinstance(timestamp, pd.DatetimeIndex):
        if timestamp.tz is None:
            return timestamp.tz_localize(NY_TZ).tz_convert('UTC')
        else:
            return timestamp.tz_convert('UTC')
    else:
        if timestamp.tz is None:
            return timestamp.tz_localize(NY_TZ).tz_convert('UTC')
        else:
            return timestamp.tz_convert('UTC')


def is_market_hours(timestamp: pd.Timestamp, session: str = 'regular') -> bool:
    """Check if timestamp falls within market hours.
    
    Args:
        timestamp: EST timestamp
        session: 'regular' (9:30-16:00), 'extended' (4:00-20:00)
        
    Returns:
        True if within market hours
    """
    time = timestamp.time()
    
    if session == 'regular':
        return time >= pd.Time(9, 30) and time <= pd.Time(16, 0)
    elif session == 'extended':
        return time >= pd.Time(4, 0) and time <= pd.Time(20, 0)
    else:
        raise ValueError("session must be 'regular' or 'extended'")


def get_trading_days(start: str, end: str) -> pd.DatetimeIndex:
    """Get trading days between start and end dates.
    
    Args:
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)
        
    Returns:
        DatetimeIndex of trading days in EST
    """
    # Create date range
    dates = pd.date_range(start=start, end=end, freq='D', tz=NY_TZ)
    
    # Filter to weekdays (Monday=0, Sunday=6)
    trading_days = dates[dates.weekday < 5]
    
    return trading_days