import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import pandas as pd
from matplotlib.ticker import MaxNLocator, FuncFormatter
from stock_animator.config.settings import AnimationConfig
import numpy as np

class AnimationBuilder:
    def __init__(self, config=AnimationConfig):
        self.config = config
        self.max_y = 0  # Holds the historical maximum value of the Y-axis

    def create_animation(self, data, symbol, formatter, **options):
        """Main method to create animation"""
        self.max_y = 0  # Reset max_y for each animation
        # Add start_capital logic
        if 'start_capital' in options and options['start_capital'] is not None:
            initial_price = data['Close'].iloc[0]
            data['Investment Value'] = (data['Close'] / initial_price) * options['start_capital']
            options['y_data'] = 'Investment Value'  # Set y_data automatically

        fig, ax = self._setup_figure()
        self._style_axes(ax)
        lines, texts = self._create_artists(ax, data, options)
        
        ani = animation.FuncAnimation(
            fig,
            self._update_animation,
            fargs=(ax, data, lines, texts, formatter, options),
            frames=self._get_frame_count(data),
            init_func=lambda: self._init_animation(ax, data, options, formatter),
            interval=1000/self.config.TARGET_FPS,
            blit=False
        )
        
        self._save_animation(ani, symbol)
        return ani

    def _setup_figure(self): 
        """Initialize matplotlib figure"""
        fig, ax = plt.subplots()
        fig.set_size_inches(*self.config.FIGURE_SIZE)
        fig.set_dpi(self.config.DPI)
        fig.patch.set_facecolor(self.config.COLORS['background'])
        fig.autofmt_xdate()
        return fig, ax

    def _style_axes(self, ax):
        """Style plot axes"""
        ax.set_facecolor(self.config.COLORS['background'])
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
            
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color(self.config.COLORS['axis'])
            ax.spines[spine].set_linewidth(1.5)
            
        ax.tick_params(axis='both', 
                      colors=self.config.COLORS['axis'],
                      labelsize=self.config.FONT_SIZE)

    def _create_artists(self, ax, data, options):
        """Create plot artists with start_capital support"""
        line, = ax.plot([], [], 
                       color=self.config.COLORS['primary'], 
                       lw=3,
                       label='Portfolio Value')
        
        line_inv = None
        text_inv = None
        if options.get('show_invested'):
            line_inv, = ax.plot([], [], 
                               color=self.config.COLORS['secondary'], 
                               lw=3,
                               alpha=0.7,
                               label='Total Invested')
            text_inv = ax.text(data.index[0], data['Total_Invested'].iloc[0], "",
                              fontsize=self.config.FONT_SIZE,
                              color=self.config.COLORS['text_secondary'],
                              fontweight='bold')
            
        text = ax.text(
            data.index[0], 
            data[options.get('y_data', 'Close')].iloc[0], 
            "",
            fontsize=self.config.FONT_SIZE,
            color=self.config.COLORS['text_primary'],
            fontweight='bold'
        )

        return (line, line_inv), (text, text_inv)

    def _init_animation(self, ax, data, options, formatter):
        """Initializes the animation"""
        y_data = options.get('y_data', 'Close')
        
        # Set X limits with offset
        initial_zoom_end = data.index[min(self.config.INITIAL_ZOOM_DAYS, len(data)-1)]
        ax.set_xlim(data.index[0], initial_zoom_end + pd.Timedelta(days=2))

        # Y limits like in the old code
        y_min = data[y_data].min().item()
        y_max = data[y_data].max().item()

        if options.get('show_invested'):
            y_min = min(y_min, data['Total_Invested'].min().item())
            y_max = max(y_max, data['Total_Invested'].max().item())

        margin = (y_max - y_min) * self.config.Y_MARGIN_PCT
        ax.set_ylim(y_min - margin, y_max + margin)

        # Axis formatting
        ax.xaxis.set_major_locator(MaxNLocator(self.config.TICK_COUNT))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m.%Y'))
        ax.yaxis.set_major_locator(MaxNLocator(self.config.TICK_COUNT))
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatter))
        
        return []

    def _update_animation(self, frame, ax, data, lines, texts, formatter, options):
        """"Update animation for each frame"""
        line, line_inv = lines
        text, text_inv = texts
        y_data = options.get('y_data', 'Close')
        start_capital = options.get('start_capital')
        show_invested = options.get('show_invested', False)

        current_index = min(frame - 1, len(data) - 1) if frame > 0 else 0
        x_last = data.index[current_index]
        y_last = data[y_data].iloc[current_index].item()

        # Update lines
        line.set_data(data.index[:frame], data[y_data][:frame])
        # Only show investment line if no start_capital
        if show_invested and line_inv and not start_capital:
            line_inv.set_data(data.index[:frame], data['Total_Invested'][:frame])

        x_range = ax.get_xlim()
        x_offset = (x_range[1] - x_range[0]) * 0.02
        x_text = x_last + pd.Timedelta(days=int(x_offset))

        # Update text FIRST (before axis adjustment)
        text.set_position((x_text, y_last))
        text.set_text(formatter(y_last, None))

        if show_invested and text_inv:
            y_inv = data['Total_Invested'].iloc[current_index].item()
            text_inv.set_position((x_text, y_inv))
            text_inv.set_text(formatter(y_inv, None))

        # THEN update axes (to keep text visible)
        self._update_dynamic_axes(ax, data, frame, show_invested, y_data)

        return self._get_return_elements(show_invested, line, line_inv, text, text_inv)

    def _update_dynamic_axes(self, ax, data, frame, show_invested, y_data):
        """Update axes dynamically based on data"""
        x_start = data.index[0]
        if frame > 1:
            visible_range = data.index[:frame]
            num_days = (visible_range[-1] - x_start).days
            scaling_factor = self.config.SCALING_FACTOR
            x_end = visible_range[-1] + pd.Timedelta(days=int(num_days * scaling_factor))
        else:
            x_end = x_start + pd.Timedelta(days=1)
        ax.set_xlim(x_start, x_end)

        current_values = data[y_data][:frame]
        min_val = current_values.min().item() if not current_values.empty else 0
        max_val = current_values.max().item() if not current_values.empty else 1

        if show_invested:
            invested_values = data['Total_Invested'][:frame]
            if not invested_values.empty:
                min_val = min(min_val, invested_values.min().item())
                max_val = max(max_val, invested_values.max().item())

        self.max_y = max(self.max_y, max_val)
        margin = (self.max_y - min_val) * self.config.Y_MARGIN_PCT
        
        ax.set_ylim(max(min_val - margin, 0), self.max_y + margin)

    def _get_return_elements(self, show_invested, *elements):
        """Returns the required graphic elements"""
        return elements if show_invested else (elements[0], elements[2])

    def _get_frame_count(self, data):
        """Determines the number of frames"""
        return min(self.config.TARGET_FRAMES, len(data))

    def _save_animation(self, ani, symbol):
        """Saves the animation as a video"""
        output_path = f'{self.config.OUTPUT_DIR}/{symbol}_animation.mp4'
        print(output_path)
        ani.save(output_path, 
                writer='ffmpeg',
                dpi=self.config.DPI,
                bitrate=8000,
                )