from stock_animator.config.settings import AnimationConfig

class CurrencyFormatter:
    def __init__(self, symbol):
        self.symbol = symbol
        
    def __call__(self, x, pos):
        # Make sure x is a scalar value
        if not isinstance(x, (int, float)):
            raise TypeError(f"Expected scalar value, got {type(x)}")
    
        if x >= 1e6:
            return f"{self.symbol}{x/1e6:.1f}M"
        elif x >= 1e3:
            value_k = x / 1e3
            if value_k < 10:
                return f"{self.symbol}{value_k:.2f}k"
            elif value_k < 100:
                return f"{self.symbol}{value_k:.1f}k"
            return f"{self.symbol}{value_k:.0f}k"
        return f"{self.symbol}{x:.0f}"