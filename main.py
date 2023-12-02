import ui
import sys

if __name__ == '__main__':
    app = ui.QApplication([])
    window = ui.MainWindow()
    window.show()
    sys.exit(app.exec())
