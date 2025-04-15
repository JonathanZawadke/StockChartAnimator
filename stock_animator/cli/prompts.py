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
    def confirm(message):
        """Get yes/no confirmation"""
        response = input(f"{message} (Y/N): ").strip().upper()
        return response == 'Y'