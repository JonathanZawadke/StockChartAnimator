from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QComboBox,
                             QDateEdit, QPushButton, QLabel, QLineEdit, QCheckBox)
from PyQt5.QtCore import QDate, QStringListModel
from stock_animator.core.data_fetcher import DataHandler
from stock_animator.core.portfolio_calculator import PortfolioCalculator
from stock_animator.visualization.animator import AnimationBuilder
from stock_animator.visualization.formatters import CurrencyFormatter
from stock_animator.gui.symbol_combo_box import SymbolComboBox
from stock_animator.gui.symbol_loader import SymbolLoader
from stock_animator.config.settings import AnimationConfig

class StockAnimatorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.config = AnimationConfig
        self.data_handler = DataHandler()
        self.portfolio_calculator = PortfolioCalculator(self.data_handler)
        self.animator = AnimationBuilder()
        self.symbol_loader = SymbolLoader("stock_animator/core/symbol.csv")
        self.init_symbol_selector()
        self.formatter = None
        self.mode_mapping = {
            0: 'P',  # Stock History
            1: 'S',  # One-time investment
            2: 'M'   # Monthly Investing
        }
        self.init_ui()

    def init_symbol_selector(self):
        self.symbol_selector = SymbolComboBox()
        self.symbol_loader.loaded.connect(self.populate_symbols)
        self.symbol_loader.start()

        # Temporary placeholders until data is loaded
        self.symbol_selector.addItems(['AAPL', 'MSFT', 'GOOG', 'AMZN'])

    def populate_symbols(self, df):
        self.symbol_selector.clear()
        model = QStringListModel()

        # Convert all values ​​explicitly to strings
        df = df.astype({'symbol': str, 'name': str})
        
        # Substitute NaN values
        df['symbol'] = df['symbol'].fillna('N/A')
        df['name'] = df['name'].fillna('Unknown')

        symbols = df['symbol'] + ' - ' + df['name']
        model.setStringList(symbols.tolist())
        
        self.symbol_selector.setModel(model)
        self.symbol_selector.setModelColumn(0)
        self.symbol_selector.setCurrentIndex(-1)

    def init_ui(self):
        # Create UI elements
        self.mode_selector = QComboBox()
        self.mode_selector.addItems([
            'Stock History',
            'One-time investment',
            'Monthly Investing'
        ])

        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addYears(-1))
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())

        self.currency_selector = QComboBox()
        self.currency_selector.addItems(['$', '€'])

        self.investment_input = QLineEdit()
        self.investment_input.setPlaceholderText('Investment amount')
        self.investment_input.hide()

        self.show_invested_check = QCheckBox('Show total invested')
        self.show_invested_check.hide()

        self.generate_btn = QPushButton('Create Animation')
        self.generate_btn.clicked.connect(self.start_animation)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Visualization Mode:'))
        layout.addWidget(self.mode_selector)
        layout.addWidget(QLabel('Stock Symbol:'))
        layout.addWidget(self.symbol_selector)
        layout.addWidget(QLabel('Start Date:'))
        layout.addWidget(self.start_date)
        layout.addWidget(QLabel('End Date:'))
        layout.addWidget(self.end_date)
        layout.addWidget(QLabel('Currency:'))
        layout.addWidget(self.currency_selector)
        layout.addWidget(self.investment_input)
        layout.addWidget(self.show_invested_check)
        layout.addWidget(self.generate_btn)

        self.setLayout(layout)
        self.setWindowTitle('Stock Animator')
        self.mode_selector.currentIndexChanged.connect(self.toggle_inputs)

    def toggle_inputs(self):
        mode_index = self.mode_selector.currentIndex()
        show_investment = mode_index in [1, 2]  # S or M
        self.investment_input.setVisible(show_investment)
        self.show_invested_check.setVisible(mode_index == 2)  # Only M

    def start_animation(self):
        try:
            # Get mode from mapping
            mode_index = self.mode_selector.currentIndex()
            mode = self.mode_mapping.get(mode_index, 'P')
            
            full_symbol = self.symbol_selector.currentText()
            symbol = full_symbol.split(" - ")[0].strip()
            start = self.start_date.date().toString('yyyy-MM-dd')
            end = self.end_date.date().toString('yyyy-MM-dd')
            currency = self.currency_selector.currentText()
            
            self.formatter = CurrencyFormatter(currency)
            
            data = self.data_handler.fetch_stock_data(symbol, start, end)
            data = self.data_handler.interpolate_data(data)

            if mode == 'P':
                self.animator.create_animation(data, symbol, self.formatter)
                
            elif mode == 'S':
                amount = float(self.investment_input.text())
                self.animator.create_animation(
                    data, symbol, self.formatter, 
                    start_capital=amount
                )
                
            elif mode == 'M':
                amount = float(self.investment_input.text())
                portfolio_data = self.portfolio_calculator.calculate(data, amount)
                self.animator.create_animation(
                    portfolio_data, 
                    symbol, 
                    self.formatter,
                    show_invested=self.show_invested_check.isChecked()
                )
                
        except Exception as e:
            print(f'Error: {str(e)}')

if __name__ == '__main__':
    app = QApplication([])
    window = StockAnimatorGUI()
    window.show()
    app.exec_()