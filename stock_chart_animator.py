import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os

max_y_value = 0
directory_path = "output"

def calculate_portfolio_value(data, monthly_investment):
    shares_owned = 0
    total_invested = 0

    dates = []
    closes = []
    invested = []
    
    for date, row in data.iterrows():
        price = float(row['Close'].item())
        shares_bought = monthly_investment / price
        shares_owned += shares_bought
        total_invested += monthly_investment
        current_value = float(shares_owned * price)

        dates.append(date)
        closes.append(current_value)
        invested.append(total_invested)
        
    portfolio_df = pd.DataFrame({
        'Close': closes,
        'Total_Invested': invested
    }, index=dates)

    # save as CSV (optional)
    portfolio_df.to_csv(f"{directory_path}/portfolio_value.csv", index=True)
    return portfolio_df


def fetch_stock_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    # save as CSV (optional)
    data.to_csv(f"{directory_path}/nvidia_stock.csv")
    return data


def create_animation(data, symbol, start_capital=None):
    fig, ax = plt.subplots()
    fig.set_size_inches(10.8, 19.2)
    fig.set_dpi(100)
    fig.autofmt_xdate()
    ax.set_title(f'{symbol} Price Animation')
    #ax.set_xlabel('Date')
    #ax.set_ylabel('Price')

    # Set background color
    ax.set_facecolor('#212121')
    fig.patch.set_facecolor('#212121')

    # Set axis color to white
    ax.spines['top'].set_visible(False)  # Hides top edge
    ax.spines['right'].set_visible(False)  # Hides right edge
    ax.spines['bottom'].set_color('#ffffff')
    ax.spines['left'].set_color('#ffffff')
    ax.tick_params(axis='x', colors='#ffffff')
    ax.tick_params(axis='y', colors='#ffffff')
    
    line, = ax.plot([], [], color='#3AFDFD', lw=2)

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
        ax.set_ylim(float(data[y_data].min().item()), float(data[y_data].max().item()))
        return line,
    
    def update(frame):
        line.set_data(data.index[:frame], data[y_data][:frame])

        # Determine the last point
        x_last = data.index[frame - 1]
        y_last = float(data[y_data].iloc[frame - 1].item())

        # Update text position
        price_text.set_position((x_last, y_last))
        price_text.set_text(f"{y_last:.0f}")

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
        if frame > 0:  # Avoid empty slices
            valid_data = data[y_data][:frame]
            
            # Calculate the min and max prices up to the current frame
            min_price = valid_data.min().item()  # Minimum price seen up to the current frame
            max_price = valid_data.max().item()  # Maximum price seen up to the current frame
            
            # Track the maximum price across all frames
            global max_y_value
            if max_y_value < max_price:
                max_y_value = max_price  # Update the global max value
            
            margin = (max_y_value - min_price) * 0.1  # Add a margin to avoid the price hitting the axis

            # Set the y-axis limits with some padding to ensure the price doesn't touch the edges
            ax.set_ylim(min_price - margin, max_y_value + margin)

        return line, price_text
    
    ani = animation.FuncAnimation(fig, update, frames=len(data), init_func=init, blit=False, interval=50)
    ani.save(f'{directory_path}/{symbol}_animation.mp4', writer='ffmpeg', dpi=100, bitrate=8000)


if __name__ == "__main__":
    symbol = "NVDA"
    start = "2020-01-01"
    end = "2025-03-30"

    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
    
    data = fetch_stock_data(symbol, start, end)

    # --- User Input for Mode Selection ---
    mode = 'price' # Default mode
    start_capital = None
    monthly_amount = None

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

            portfolio_df = calculate_portfolio_value(data, monthly_amount)
            create_animation(portfolio_df, symbol, None)
        except:
            print(f"An error occurred.")
            mode = 'price'
    elif investment_type == 'P':
        mode = 'price'
        create_animation(data, symbol, None)

    elif investment_type == 'Q':
        print("Exiting.")
        exit()