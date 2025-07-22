from PyQt5.QtWidgets import QApplication
import sys
from ui.main_window import DownloaderApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DownloaderApp()
    win.show()
    sys.exit(app.exec_())
