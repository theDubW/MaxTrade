import sys

#QT imports
from PySide2.QtWidgets import QApplication, QDockWidget
# from PySide2.QtCore import Qt


#Custom Widgets
from StockPositions import StockPositions
from MainWindow import MainWindow

#Helper Module
import robinhoodBot as r

if __name__ == '__main__':
    r.login()
    app = QApplication(sys.argv)
    stockWidget = StockPositions()
    stockWidget.startTimer()
    window = MainWindow(stockWidget)
    window.show()

    sys.exit(app.exec_())