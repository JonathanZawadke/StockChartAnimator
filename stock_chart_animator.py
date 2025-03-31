import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def fetch_stock_data(symbol, start, end):
    data = yf.download(symbol, start=start, end=end)
    # save as CSV (optional)
    data.to_csv("output/nvidia_stock.csv")
    return data


def create_animation(data, symbol):
    fig, ax = plt.subplots()
    fig.set_size_inches(19.2, 10.8)
    fig.set_dpi(100)
    ax.set_title(f'{symbol} Price Animation')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    
    line, = ax.plot([], [], 'b-', lw=2)
    
    def init():
        ax.set_xlim(data.index[0], data.index[-1])
        ax.set_ylim(float(data['Close'].min()), float(data['Close'].max()))
        return line,
    
    def update(frame):
        line.set_data(data.index[:frame], data['Close'][:frame])
        return line,
    
    ani = animation.FuncAnimation(fig, update, frames=len(data), init_func=init, blit=False, interval=50)
    ani.save(f'output/{symbol}_animation.mp4', writer='ffmpeg', dpi=100, bitrate=8000)
    plt.show()


if __name__ == "__main__":
    symbol = "NVDA"
    start = "2020-01-01"
    end = "2025-03-30"
    
    data = fetch_stock_data(symbol, start, end)
    
    create_animation(data, symbol)
