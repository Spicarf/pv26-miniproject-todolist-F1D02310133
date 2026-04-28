"""
main.py
Entry point aplikasi Task Manager Pro.

Cara menjalankan:
    python main.py

Requirements:
    pip install PySide6
"""

import sys
import os

# Pastikan package lokal bisa di-import dari mana pun dijalankan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import MainWindow


def load_stylesheet(app: QApplication):
    """Memuat file QSS eksternal untuk styling global."""
    qss_path = os.path.join(BASE_DIR, "styles", "style.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[WARNING] File QSS tidak ditemukan: {qss_path}")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Task Manager Pro")
    app.setApplicationVersion("1.0.0")

    # Font default
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
