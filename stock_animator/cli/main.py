from ..core.data_fetcher import DataHandler
from ..core.portfolio_calculator import PortfolioCalculator
from ..visualization.animator import AnimationBuilder
from ..visualization.formatters import CurrencyFormatter
from ..cli.prompts import CLIPrompter
from stock_animator.config.settings import AnimationConfig

class StockAnimatorCLI:
    def __init__(self):
        self.config = AnimationConfig
        self.data_handler = DataHandler()
        self.portfolio_calculator = PortfolioCalculator(self.data_handler)
        self.animator = AnimationBuilder()
        
    def run(self):
        """Main application loop"""
        currency = CLIPrompter.get_currency()
        formatter = CurrencyFormatter(currency)
        
        while True:
            choice = CLIPrompter.get_visualization_mode()
            if choice == 'Q':
                break
            stock_symbol = CLIPrompter.get_stock_symbol()
            start_str, end_str = CLIPrompter.get_date_range()
            data = self._initialize_data(stock_symbol, start_str, end_str)
            self._handle_choice(choice, data, formatter, stock_symbol)

    def _initialize_data(self, stock_symbol, start_str, end_str):
        """Fetch and prepare base data"""
        data = self.data_handler.fetch_stock_data(stock_symbol, start_str, end_str)
        return self.data_handler.interpolate_data(data)

    def _handle_choice(self, choice, data, formatter, stock_symbol):
        """Route user choice to appropriate handler"""
        handlers = {
            'P': self._handle_price,
            'S': self._handle_single,
            'M': self._handle_monthly
        }
        handlers.get(choice, self._handle_invalid)(data, formatter, stock_symbol)

    def _handle_price(self, data, formatter, stock_symbol):
        """Handle price-only visualization"""
        self.animator.create_animation(data, stock_symbol, formatter)

    def _handle_single(self, data, formatter, stock_symbol):
        """Handle single investment scenario"""
        amount = CLIPrompter.get_investment_amount("Initial investment amount (e.g. 1000): ")
        self.animator.create_animation(data, stock_symbol, formatter, start_capital=amount)

    def _handle_monthly(self, data, formatter, stock_symbol):
        """Handle monthly investment scenario"""
        amount = CLIPrompter.get_investment_amount("Monthly investment amount (e.g. 100): ")
        show_invested = CLIPrompter.confirm("Show total invested line?")
        portfolio_data = self.portfolio_calculator.calculate(data, amount)
        self.animator.create_animation(portfolio_data, stock_symbol, formatter, show_invested=show_invested)

    def _handle_invalid(self, *args):
        print("Invalid selection")

if __name__ == "__main__":
    app = StockAnimatorCLI()
    app.run()