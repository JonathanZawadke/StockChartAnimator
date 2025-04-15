from pathlib import Path

class AnimationConfig:
    # Technical Settings
    TARGET_FPS = 30
    TARGET_DURATION = 60  # in seconds
    TARGET_FRAMES = TARGET_FPS * TARGET_DURATION
    OUTPUT_DIR = Path("output")
    
    # Visual Settings
    FIGURE_SIZE = (10.8, 19.2)
    DPI = 100
    FONT_SIZE = 12
    INITIAL_ZOOM_DAYS = 60
    TICK_COUNT = 5
    
    # Color Scheme
    COLORS = {
        'primary': '#3AFDFD',
        'secondary': '#FF69B4',
        'background': '#212121',
        'axis': '#FFFFFF',
        'text_primary': '#3AFDFD',
        'text_secondary': '#FF69B4'
    }
    
    # Animation Parameters
    X_OFFSET_PCT = 0.02
    Y_MARGIN_PCT = 0.1
    INVESTMENT_SMOOTHING_FRAMES = 10
    SCALING_FACTOR = 0.1