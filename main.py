# ======================================================================
# Script: main.py
# Description: Digital Signature App - Main Entry Point
# ======================================================================

import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Optionally set application metadata
    app.setApplicationName("Digital Signature")
    app.setApplicationVersion("1.0.0")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()