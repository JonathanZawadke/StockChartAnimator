import yfinance as yf
import pandas as pd
from pathlib import Path
from stock_animator.config.settings import AnimationConfig

class DataHandler:
    def __init__(self, config=AnimationConfig):
        self.config = config
        self._ensure_output_dir()
        
    def _ensure_output_dir(self):
        self.config.OUTPUT_DIR.mkdir(exist_ok=True)
        
    def fetch_stock_data(self, symbol, start, end):
        """Fetch stock data from Yahoo Finance"""
        data = yf.download(
            symbol, 
            start=start, 
            end=end,
            auto_adjust=True
            )
        return data
    
    def interpolate_data(self, data):
        """Interpolate data to target frame count"""
        new_index = pd.date_range(
            start=data.index.min(),
            end=data.index.max(),
            periods=self.config.TARGET_FRAMES
        )
        return data.reindex(data.index.union(new_index)) \
                 .interpolate(method='time') \
                 .reindex(new_index)