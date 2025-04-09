import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import os
from matplotlib.ticker import MaxNLocator

max_y_value = 0
directory_path = "output"
TARGET_FRAMES = 1800  # 60 seconds with 30 FPS

def interpolate_data(data, target_length=TARGET_FRAMES):
    # Interpolates the data to the desired number of frames.
    new_index = pd.date_range(start=data.index.min(), end=data.index.max(), periods=target_length)
    data_interpolated = data.reindex(data.index.union(new_index)).interpolate(method='time').reindex(new_index)
    return data_interpolated


def calculate_portfolio_value(data, monthly_investment):
    shares_owned = 0
    total_invested = 0
    dates = []
    closes = []
    invested = []
    
    # Find the first trading day of each month
    monthly_dates = []
    current_month = None

    # First pass: Identify investment days
    for date in data.index:
        if date.month != current_month:
            monthly_dates.append(date)
            current_month = date.month
    
    # Second pass: Create smooth investment steps
    investment_steps = {}
    for i, invest_date in enumerate(monthly_dates):
        # Distribute investment over 10 frames (0.5% of total animation)
        start_frame = data.index.get_loc(invest_date)
        end_frame = min(start_frame + 10, len(data)-1)
        
        for frame in range(start_frame, end_frame+1):
            fraction = (frame - start_frame) / (end_frame - start_frame)
            investment_steps[frame] = monthly_investment * fraction
    
    # Third pass: Calculate values
    for frame, (date, row) in enumerate(data.iterrows()):
        # Add partial investments
        if frame in investment_steps:
            price = float(row['Close'])
            shares_bought = investment_steps[frame] / price
            shares_owned += shares_bought
            total_invested += investment_steps[frame]
        
        current_value = shares_owned * float(row['Close'])
        dates.append(date)
        closes.append(current_value)
        invested.append(total_invested)
    
    portfolio_df = pd.DataFrame({'Close': closes, 'Total_Invested': invested}, index=dates)
    portfolio_df = interpolate_data(portfolio_df)
    portfolio_df.to_csv(f"{directory_path}/portfolio_value.csv", index=True)
    return portfolio_df


def ask_show_invested():
    response = input("Show total invested line? (Y/N): ").strip().upper()
    return response == 'Y'


def create_currency_formatter(symbol):
    """Creates a currency formatting function with the selected symbol"""
    def currency_formatter(x, pos):
        if x >= 1e6:
            return f"{symbol}{x/1e6:.1f}M"
        elif x >= 1e3:
            value_k = x / 1e3
            if value_k < 10:
                # 1.000-9.999: 2 Decimals (e.g. 1,23k)
                return f"{symbol}{value_k:.2f}k"
            elif value_k < 100:
                # 10.000-99.999: 1 Decimals (e.g. 10,1k)
                return f"{symbol}{value_k:.1f}k"
            else:
                # from 100.000: no Decimals (e.g. 100k)
                return f"{symbol}{value_k:.0f}k"
        else:
            # Unter 1.000: whole number (e.g. 999)
            return f"{symbol}{x:.0f}"
    return currency_formatter
    

def calculate_interval(data):
    total_frames = len(data)
    target_duration = 61
    
    # Calculate the interval between each frame to ensure the video duration is ~1 minute
    interval = int(target_duration * 1000 / total_frames)  # In milliseconds

    return interval


def fetch_stock_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    # save as CSV (optional)
    data.to_csv(f"{directory_path}/nvidia_stock.csv")
    return data


def create_animation(data, symbol, start_capital=None, show_invested=False):
    fig, ax = plt.subplots()
    fig.set_size_inches(10.8, 19.2)
    fig.set_dpi(100)
    fig.autofmt_xdate()
    ax.set_title(f'{symbol} Price Animation', fontsize=16, color='#ffffff', fontweight='bold')
    #ax.set_xlabel('Date')
    #ax.set_ylabel('Price')

    # Set background color
    ax.set_facecolor('#212121')
    fig.patch.set_facecolor('#212121')

    # Set axis color to white
    ax.spines['top'].set_visible(False)  # Hides top edge
    ax.spines['right'].set_visible(False)  # Hides right edge
    for spine in ['bottom', 'left']:
        ax.spines[spine].set_color('#ffffff')
        ax.spines[spine].set_linewidth(1.5)

    ax.tick_params(axis='x', colors='#ffffff', labelsize=12)
    ax.tick_params(axis='y', colors='#ffffff', labelsize=12)
    
    line, = ax.plot([], [], color='#3AFDFD', lw=4)
    line_invested = None
    text_invested = None

    if show_invested:
        line_invested, = ax.plot([], [], color='#FF69B4', lw=4)
        text_invested = ax.text(data.index[0], data['Total_Invested'].iloc[0], 
                              "", fontsize=12, color='#FF69B4', fontweight='bold')

    # Use investment calculation if start_capital is set
    if start_capital is not None:
        initial_price = data['Close'].iloc[0]
        data['Investment Value'] = (data['Close'] / initial_price) * start_capital
        y_data = 'Investment Value'
    else:
        y_data = 'Close'

    # Initialize the text element for the last price value
    price_text = ax.text(data.index[0], data[y_data].iloc[0], 
                         f"{data[y_data].iloc[0].item():.2f}",
                         fontsize=12, color='#3AFDFD', fontweight='bold')
    
    # Initialize the limits for the x-axis (to zoom in initially)
    initial_zoom_period = 60  # Number of days to initially show (for zoom effect)
    ax.set_xlim(data.index[0], data.index[initial_zoom_period])  # Start with zoomed-in view
    ax.set_ylim(float(data[y_data].min().item()), float(data[y_data].max().item()))

    def init():
        # Set the initial zoom on the X-axis (show first few months)
        ax.set_xlim(data.index[0], data.index[initial_zoom_period])

        # Calculate Y limits for both lines
        y_min = data[y_data].min().item()
        y_max = data[y_data].max().item()
        if show_invested:
            y_min = min(y_min, data['Total_Invested'].min().item())
            y_max = max(y_max, data['Total_Invested'].max().item())
        
        ax.set_ylim(y_min, y_max)
        
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))  # max 6 Ticks on X-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%Y'))

        ax.yaxis.set_major_locator(MaxNLocator(nbins=5))  # max 6 Ticks on Y-axis
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(currency_formatter))

        return (line, line_invested) if show_invested else (line,)

    def update(frame):
        line.set_data(data.index[:frame], data[y_data][:frame])

       # Determine the last point
        x_last = data.index[frame - 1]
        y_last = float(data[y_data].iloc[frame - 1].item())

        # Add small offset to x position of price text
        x_range = ax.get_xlim()
        x_offset_pct = 0.02  # 2% offset for both texts
        x_offset = (x_range[1] - x_range[0]) * x_offset_pct
        x_text = x_last + pd.Timedelta(days=int(x_offset))

        # Update portfolio text position
        price_text.set_position((x_text, y_last))
        price_text.set_text(currency_formatter(y_last, None))

        # Update investment text if shown
        if show_invested:
            line_invested.set_data(data.index[:frame], data['Total_Invested'][:frame])
            
            y_last_invested = data['Total_Invested'].iloc[frame-1].item()
            text_invested.set_position((x_text, y_last_invested))
            text_invested.set_text(currency_formatter(y_last_invested, None))

        # Dynamic x-axis scaling
        x_start = data.index[0]  # The beginning of the chart always remains visible
        if frame > 1:
            visible_range = data.index[:frame]
            num_days = (visible_range[-1] - visible_range[0]).days
            scaling_factor = 0.1  # 10 % additional space
            right_offset = pd.Timedelta(days=int(num_days * scaling_factor))
            x_end = data.index[frame - 1] + right_offset
        else:
            x_end = data.index[frame - 1]  # No offset if there is too little data

        ax.set_xlim(x_start, x_end)

        # Dynamically adjust the y-axis limits based on the price data
        # Ensure that there is data to calculate min and max
        if frame > 0:
            current_values = data[y_data][:frame]
            min_price = current_values.min().item()
            max_price = current_values.max().item()
            
            if show_invested:
                invested_values = data['Total_Invested'][:frame]
                min_price = min(min_price, invested_values.min().item())
                max_price = max(max_price, invested_values.max().item())

            global max_y_value
            max_y_value = max(max_y_value, max_price)
            margin = (max_y_value - min_price) * 0.1
            
            ax.set_ylim(min_price - margin, max_y_value + margin)

        return (line, line_invested, text_invested) if show_invested else (line, text_invested)
    

    interval = 1000 / 30
    
    ani = animation.FuncAnimation(fig, update, 
                                  frames=TARGET_FRAMES if len(data) > TARGET_FRAMES else len(data), 
                                  init_func=init, 
                                  blit=False, 
                                  interval=interval
                                  )
    ani.save(f'{directory_path}/{symbol}_animation.mp4', writer='ffmpeg', dpi=100, bitrate=8000)


def ask_currency():
    """Asks the user for the desired currency"""
    while True:
        currency = input("Select currency (€/$): ").strip().upper()
        if currency in ['€', '$']:
            return currency
        print("Invalid currency. Please enter € or $.")

if __name__ == "__main__":
    symbol = "NVDA"
    start = "2024-09-01"
    end = "2025-03-30"

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    data = fetch_stock_data(symbol, start, end)
    data = interpolate_data(data)

    # --- User Input for Mode Selection ---
    mode = 'price' # Default mode
    start_capital = None
    monthly_amount = None

    currency_symbol = ask_currency()
    currency_formatter = create_currency_formatter(currency_symbol)

    print("\nSelect visualization type:")
    print("  P: Show stock price only")
    print("  S: Simulate a single initial investment")
    print("  M: Simulate recurring monthly investments")
    # Added an option to just exit
    print("  Q: Quit")
    investment_type = input("Enter choice (P/S/M/Q): ").strip().upper()

    # --- Process User Choice ---
    if investment_type == 'S':
        mode = 'single'
        try:
            start_capital = float(input("Enter initial investment amount (e.g., 1000): "))
            if start_capital <= 0: raise ValueError("Investment must be positive.")

            create_animation(data, symbol, start_capital)

        except ValueError as e:
            print(f"Invalid input: {e}. Showing stock price instead.")
            mode = 'price'

    elif investment_type == 'M':
        mode = 'monthly'
        try:
            monthly_amount = float(input("Enter monthly investment amount (e.g., 100): "))
            if monthly_amount <= 0: raise ValueError("Monthly investment must be positive.")

            show_invested = ask_show_invested()
            portfolio_df = calculate_portfolio_value(data, monthly_amount)
            create_animation(portfolio_df, symbol, None, show_invested)
        except Exception as e:
            print(f"An error occurred. ${e}.")
            mode = 'price'
    elif investment_type == 'P':
        mode = 'price'
        create_animation(data, symbol, None)

    elif investment_type == 'Q':
        print("Exiting.")
        exit()