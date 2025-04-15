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
        data = self._initialize_data()
        currency = CLIPrompter.get_currency()
        formatter = CurrencyFormatter(currency)
        
        while True:
            choice = CLIPrompter.get_visualization_mode()
            if choice == 'Q':
                break
            self._handle_choice(choice, data, formatter)

    def _initialize_data(self):
        """Fetch and prepare base data"""
        data = self.data_handler.fetch_stock_data("AMZN", "2020-05-01", "2025-03-30")
        return self.data_handler.interpolate_data(data)

    def _handle_choice(self, choice, data, formatter):
        """Route user choice to appropriate handler"""
        handlers = {
            'P': self._handle_price,
            'S': self._handle_single,
            'M': self._handle_monthly
        }
        handlers.get(choice, self._handle_invalid)(data, formatter)

    def _handle_price(self, data, formatter):
        """Handle price-only visualization"""
        self.animator.create_animation(data, "AMZN", formatter)

    def _handle_single(self, data, formatter):
        """Handle single investment scenario"""
        amount = CLIPrompter.get_investment_amount("Initial investment amount (e.g. 1000): ")
        self.animator.create_animation(data, "AMZN", formatter, start_capital=amount)

    def _handle_monthly(self, data, formatter):
        """Handle monthly investment scenario"""
        amount = CLIPrompter.get_investment_amount("Monthly investment amount (e.g. 100): ")
        show_invested = CLIPrompter.confirm("Show total invested line?")
        portfolio_data = self.portfolio_calculator.calculate(data, amount)
        self.animator.create_animation(portfolio_data, "AMZN", formatter, show_invested=show_invested)

    def _handle_invalid(self, *args):
        print("Invalid selection")

if __name__ == "__main__":
    app = StockAnimatorCLI()
    app.run()