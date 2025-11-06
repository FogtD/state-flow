import sys
from PyQt5.QtWidgets import QApplication
from ui.start_select_menu import StartupMenu

if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_w = StartupMenu()
    start_w.show()
    sys.exit(app.exec_())