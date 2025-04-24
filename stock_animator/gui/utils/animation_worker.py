from PyQt5.QtCore import QThread, pyqtSignal

class AnimationWorker(QThread):
    update_progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, animator, data, symbol, formatter, portfolio_calculator, show_invested, mode, amount):
        super().__init__()
        self.animator = animator
        self.data = data
        self.symbol = symbol
        self.formatter = formatter
        self.portfolio_calculator = portfolio_calculator
        self.show_invested = show_invested
        self.mode = mode
        self.amount = amount

    def run(self):
        try:
            # Portfolio calculation for Mode M
            if self.mode == 'M':
                self.data = self.portfolio_calculator.calculate(
                    self.data,
                    self.amount
                )

            self.animator.progress_callback = self.update_progress.emit
            ani = self.animator.create_animation(
                self.data,
                self.symbol,
                self.formatter,
                show_invested=self.show_invested
            )

            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))