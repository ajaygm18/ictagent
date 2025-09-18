"""Data loading from various sources (yfinance, CSV)."""

from typing import Optional, Dict, Any
import pandas as pd
import yfinance as yf
from ictagent.utils.timezones import ensure_est_timezone


def load_yfinance(symbol: str, timeframe: str = "5m", 
                 start: Optional[str] = None, end: Optional[str] = None,
                 **kwargs) -> pd.DataFrame:
    """Download intraday OHLCV from yfinance with EST timezone.
    
    Args:
        symbol: Trading symbol (e.g., 'ES=F', 'EURUSD=X')
        timeframe: Data interval ('1m', '5m', '15m', '1h', '1d')
        start: Start date string (YYYY-MM-DD)
        end: End date string (YYYY-MM-DD)
        **kwargs: Additional yfinance.download parameters
        
    Returns:
        DataFrame with OHLCV data in EST timezone
        
    Notes:
        - yfinance intraday limitations: 1m ~7 days, 5m/15m ~60 days
        - For longer backtests, use daily data or CSV files
    """
    # Set default date range if not provided
    if start is None and timeframe in ['1m', '5m', '15m']:
        # Use reasonable defaults based on yfinance limitations
        if timeframe == '1m':
            start = pd.Timestamp.now() - pd.Timedelta(days=7)
        else:
            start = pd.Timestamp.now() - pd.Timedelta(days=60)
        start = start.strftime('%Y-%m-%d')
    
    # Download data
    try:
        df = yf.download(
            symbol, 
            interval=timeframe, 
            start=start, 
            end=end,
            auto_adjust=False,
            prepost=True,  # Include pre/post market data
            progress=False,
            **kwargs
        )
    except Exception as e:
        raise RuntimeError(f"Failed to download data for {symbol}: {str(e)}")
    
    if df.empty:
        raise ValueError(f"No data returned for {symbol} {timeframe} {start} to {end}")
    
    # Handle multi-level columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)  # Remove symbol level
    
    # Standardize column names
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # Remove adjusted close if present
    if 'adj_close' in df.columns:
        df = df.drop(columns=['adj_close'])
    
    # Ensure we have required OHLCV columns
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Convert to EST timezone
    df = ensure_est_timezone(df)
    
    # Remove any duplicate timestamps
    df = df[~df.index.duplicated(keep='first')]
    
    print(f"Loaded {len(df)} bars for {symbol} from {df.index[0]} to {df.index[-1]}")
    
    return df


def load_csv(filepath: str, datetime_col: str = 'datetime', 
            timezone: str = 'America/New_York', **kwargs) -> pd.DataFrame:
    """Load OHLCV data from CSV file.
    
    Args:
        filepath: Path to CSV file
        datetime_col: Name of datetime column
        timezone: Timezone for datetime column
        **kwargs: Additional pd.read_csv parameters
        
    Returns:
        DataFrame with OHLCV data in EST timezone
    """
    # Load CSV
    df = pd.read_csv(filepath, **kwargs)
    
    # Set datetime index
    if datetime_col in df.columns:
        df[datetime_col] = pd.to_datetime(df[datetime_col])
        df = df.set_index(datetime_col)
    elif df.index.name == datetime_col or isinstance(df.index, pd.DatetimeIndex):
        df.index = pd.to_datetime(df.index)
    else:
        raise ValueError(f"Datetime column '{datetime_col}' not found")
    
    # Standardize column names
    df.columns = [col.lower().replace(' ', '_') for col in df.columns]
    
    # Ensure required columns exist
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Set timezone
    if df.index.tz is None:
        df.index = df.index.tz_localize(timezone)
    else:
        df.index = df.index.tz_convert('America/New_York')
    
    return df


def get_symbol_info(symbol: str) -> Dict[str, Any]:
    """Get basic information about a trading symbol.
    
    Args:
        symbol: Trading symbol
        
    Returns:
        Dictionary with symbol information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'exchange': info.get('exchange', 'Unknown'),
            'currency': info.get('currency', 'USD'),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap', None)
        }
    except Exception as e:
        print(f"Warning: Could not fetch info for {symbol}: {e}")
        return {'symbol': symbol, 'name': symbol, 'exchange': 'Unknown'}