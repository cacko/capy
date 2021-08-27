from PyQt6.QtGui import QIcon
from gui import App
from PyQt6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        icon = QIcon()
        icon.addFile('capy.png')
        app.setWindowIcon(icon)
        a = App()
        a.show()
        sys.exit(app.exec())
    except KeyboardInterrupt:
        pass
