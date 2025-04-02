import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

max_y_value = 0

def fetch_stock_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    # save as CSV (optional)
    data.to_csv("output/nvidia_stock.csv")
    return data


def create_animation(data, symbol):
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

    # Initialize the text element for the last price value
    price_text = ax.text(data.index[0], data['Close'].iloc[0], 
                         f"{data['Close'].iloc[0].item():.2f}",
                         fontsize=12, color='#3AFDFD', fontweight='bold')
    
    # Initialize the limits for the x-axis (to zoom in initially)
    initial_zoom_period = 60  # Number of days to initially show (for zoom effect)
    ax.set_xlim(data.index[0], data.index[initial_zoom_period])  # Start with zoomed-in view
    ax.set_ylim(float(data['Close'].min().item()), float(data['Close'].max().item()))

    def init():
        # Set the initial zoom on the X-axis (show first few months)
        ax.set_xlim(data.index[0], data.index[initial_zoom_period])
        ax.set_ylim(float(data['Close'].min().item()), float(data['Close'].max().item()))
        return line,
    
    def update(frame):
        line.set_data(data.index[:frame], data['Close'][:frame])

        # Determine the last point
        x_last = data.index[frame - 1]
        y_last = float(data['Close'].iloc[frame - 1].item())

        # Update text position
        price_text.set_position((x_last, y_last))
        price_text.set_text(f"{y_last:.2f}")

        # Dynamische Skalierung der x-Achse
        x_start = data.index[0]  # Anfang des Charts bleibt immer sichtbar
        x_end = data.index[frame]  # Ende bleibt fixiert
        ax.set_xlim(x_start, x_end)

        # Dynamically adjust the y-axis limits based on the price data
        # Ensure that there is data to calculate min and max
        if frame > 0:  # Avoid empty slices
            valid_data = data['Close'][:frame]
            
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
    ani.save(f'output/{symbol}_animation.mp4', writer='ffmpeg', dpi=100, bitrate=8000)


if __name__ == "__main__":
    symbol = "NVDA"
    start = "2020-01-01"
    end = "2025-03-30"
    
    data = fetch_stock_data(symbol, start, end)
    
    create_animation(data, symbol)
