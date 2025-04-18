import sys
from PyQt6.QtWidgets import QApplication
from gui import FatturaRenamer

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FatturaRenamer()
    window.show()
    sys.exit(app.exec())