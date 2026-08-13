import sys

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow
from ui.styles import STYLE_SHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE_SHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
