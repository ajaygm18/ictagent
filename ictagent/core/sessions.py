"""ICT session management with EST/DST awareness."""

import pandas as pd
from typing import Tuple
from datetime import time

NY_TZ = "America/New_York"


class SessionManager:
    """Manage ICT trading sessions with DST-aware EST timing."""
    
    @staticmethod
    def in_time_window(index: pd.DatetimeIndex, start_hm: Tuple[int, int], 
                      end_hm: Tuple[int, int]) -> pd.Series:
        """Return boolean mask for timestamps within [start, end) in EST.
        
        Args:
            index: DatetimeIndex (will be converted to EST)
            start_hm: (hour, minute) tuple for start time
            end_hm: (hour, minute) tuple for end time
            
        Returns:
            Boolean Series mask
        """
        # Convert to EST if needed
        if index.tz is None:
            idx_est = index.tz_localize(NY_TZ)
        else:
            idx_est = index.tz_convert(NY_TZ)
        
        start_time = time(start_hm[0], start_hm[1])
        end_time = time(end_hm[0], end_hm[1])
        
        current_times = idx_est.time
        
        if start_time <= end_time:
            # Normal case: start and end on same day
            mask = (current_times >= start_time) & (current_times < end_time)
        else:
            # Overnight session: spans midnight
            mask = (current_times >= start_time) | (current_times < end_time)
            
        return pd.Series(mask, index=index)
    
    @classmethod
    def premarket_session(cls, index: pd.DatetimeIndex) -> pd.Series:
        """Pre-market session: 02:00-07:00 EST."""
        return cls.in_time_window(index, (2, 0), (7, 0))
    
    @classmethod
    def ny_open_session(cls, index: pd.DatetimeIndex) -> pd.Series:
        """NY market open: 09:30-10:00 EST."""
        return cls.in_time_window(index, (9, 30), (10, 0))
    
    @classmethod
    def ny_killzone(cls, index: pd.DatetimeIndex) -> pd.Series:
        """NY Killzone (Silver Bullet): 10:00-11:00 EST."""
        return cls.in_time_window(index, (10, 0), (11, 0))
    
    @classmethod
    def london_ny_overlap(cls, index: pd.DatetimeIndex) -> pd.Series:
        """London-NY overlap: 08:00-11:00 EST."""
        return cls.in_time_window(index, (8, 0), (11, 0))
    
    @classmethod
    def power_hour(cls, index: pd.DatetimeIndex) -> pd.Series:
        """Power Hour: 14:00-15:00 EST."""
        return cls.in_time_window(index, (14, 0), (15, 0))
    
    @classmethod
    def afternoon_session(cls, index: pd.DatetimeIndex) -> pd.Series:
        """Afternoon session: 13:00-16:00 EST."""
        return cls.in_time_window(index, (13, 0), (16, 0))
    
    @classmethod
    def get_session_mask(cls, index: pd.DatetimeIndex, session: str) -> pd.Series:
        """Get session mask by name.
        
        Args:
            index: DatetimeIndex
            session: Session name ('premarket', 'ny_open', 'killzone', 
                    'london_ny', 'power_hour', 'afternoon')
                    
        Returns:
            Boolean mask for session
        """
        session_map = {
            'premarket': cls.premarket_session,
            'ny_open': cls.ny_open_session,
            'killzone': cls.ny_killzone,
            'london_ny': cls.london_ny_overlap,
            'power_hour': cls.power_hour,
            'afternoon': cls.afternoon_session
        }
        
        if session not in session_map:
            raise ValueError(f"Unknown session: {session}. Available: {list(session_map.keys())}")
            
        return session_map[session](index)