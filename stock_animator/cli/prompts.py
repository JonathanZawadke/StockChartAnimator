from datetime import datetime

class CLIPrompter:
    @staticmethod
    def get_currency():
        """Get currency selection from user"""
        while True:
            currency = input("Select currency (€/$): ").strip().upper()
            if currency in ['€', '$']:
                return currency
            print("Invalid input. Please enter € or $.")

    @staticmethod
    def get_visualization_mode():
        """Get visualization mode selection"""
        print("\nSelect visualization type:")
        print("  P: Show stock price only")
        print("  S: Simulate single initial investment")
        print("  M: Simulate monthly investments")
        print("  Q: Quit")
        return input("Enter choice (P/S/M/Q): ").strip().upper()

    @staticmethod
    def get_investment_amount(prompt):
        """Get numeric investment amount"""
        while True:
            try:
                amount = float(input(prompt))
                if amount > 0:
                    return amount
                print("Amount must be positive.")
            except ValueError:
                print("Invalid number format.")

    @staticmethod
    def get_stock_symbol():
        """Get Symbol name of the stock"""
        symbol = input("Enter stock symbol (e.g. AMZN): ").strip().upper()
        return symbol
    
    @staticmethod
    def get_date_range():
        """Get start and end date in YYYY-MM-DD format"""
        date_format = "%Y-%m-%d"
        while True:
            try:
                start_str = input("Enter start date (YYYY-MM-DD): ").strip()
                start_date = datetime.strptime(start_str, date_format)
                
                end_str = input("Enter end date (YYYY-MM-DD): ").strip()
                end_date = datetime.strptime(end_str, date_format)

                if start_date > end_date:
                    print("Error: End date must be after start date")
                    continue
                    
                return start_str, end_str
                
            except ValueError as e:
                print(f"Invalid date format. Please use YYYY-MM-DD. Error: {e}")

    @staticmethod
    def confirm(message):
        """Get yes/no confirmation"""
        response = input(f"{message} (Y/N): ").strip().upper()
        return response == 'Y'