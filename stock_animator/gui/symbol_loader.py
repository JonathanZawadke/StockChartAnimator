import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import os

class SymbolLoader(QThread):
    loaded = pyqtSignal(pd.DataFrame)

    def __init__(self, file_path):
        super().__init__()
        if getattr(sys, 'frozen', False):
            # Path in the bundled program
            base_path = sys._MEIPASS
            self.file_path = os.path.join(base_path, file_path)
        else:
            # Path in development mode
            self.file_path = file_path

    def run(self):
        try:
            # Assumption: CSV with columns 'symbol' and 'name'
            df = pd.read_csv(self.file_path)
            self.loaded.emit(df)
        except FileNotFoundError:
            # Fallback to dummy data
            df = pd.DataFrame({
                'symbol': ['AAPL', 'MSFT', 'GOOG', 'AMZN'],
                'name': ['Apple Inc', 'Microsoft', 'Alphabet', 'Amazon']
            })
            self.loaded.emit(df)