import pandas as pd
from config.settings import AnimationConfig

class PortfolioCalculator:
    def __init__(self, data_handler):
        self.data_handler = data_handler
        self.config = AnimationConfig
        
    def calculate(self, data, monthly_investment):
        """Calculate portfolio value with monthly investments"""
        shares_owned = 0
        total_invested = 0
        dates, closes, invested = [], [], []
        
        monthly_dates = self._get_monthly_dates(data)
        investment_steps = self._calculate_investment_steps(data, monthly_dates, monthly_investment)
        
        for frame, (date, row) in enumerate(data.iterrows()):
            shares_owned, total_invested = self._process_frame(frame, row, investment_steps, shares_owned, total_invested)
            current_value = shares_owned * float(row['Close'])
            dates.append(date)
            closes.append(current_value)
            invested.append(total_invested)
            
        return self._create_portfolio_df(dates, closes, invested)

    def _get_monthly_dates(self, data):
        """Identify first trading day of each month"""
        monthly_dates = []
        current_month = None
        for date in data.index:
            if date.month != current_month:
                monthly_dates.append(date)
                current_month = date.month
        return monthly_dates
    
    def _calculate_investment_steps(self, data, dates, investment):
        """Distribute investments over multiple frames"""
        steps = {}
        for date in dates:
            start = data.index.get_loc(date)
            end = min(start + self.config.INVESTMENT_SMOOTHING_FRAMES, len(data)-1)
            num_frames = end - start + 1
            for frame in range(start, end + 1):
                steps[frame] = investment / num_frames
        return steps
    
    def _process_frame(self, frame, row, steps, shares_owned, total_invested):
        """Process individual animation frame"""
        if frame in steps:
            price = float(row['Close'])
            shares_bought = steps[frame] / price
            shares_owned += shares_bought
            total_invested += steps[frame]
        return shares_owned, total_invested
    
    def _create_portfolio_df(self, dates, closes, invested):
        """Create and interpolate portfolio DataFrame"""
        # Ensure unique dates by aggregating duplicates
        df = pd.DataFrame({
            'Close': closes,
            'Total_Invested': invested
        }, index=dates)
        
        # 3. Save with clean format
        df.to_csv("output/portfolio_value.csv", 
                index=True, 
                index_label='Date', 
                float_format='%.4f')
        
        return self.data_handler.interpolate_data(df)