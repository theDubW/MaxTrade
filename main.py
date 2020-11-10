import sys

#QT imports
from PySide2.QtWidgets import QApplication, QDockWidget, QDialog

import login as l


#Custom Widgets
from StockPositions import StockPositions
from OptionPositions import OptionPositions
from MainWindow import MainWindow

#Helper Module
import robinhoodBot as r

if __name__ == '__main__':
    robinhood = r.Robinhood()
    isLoggedIn = False
    try:
        isLoggedIn = robinhood.login()
    except:
        isLoggedIn = False
    app = QApplication(sys.argv)
    if(isLoggedIn == False):
        login = l.Login()
        if(login.exec_()==QDialog.Accepted):
            stockWidget = StockPositions()
            stockWidget.startTimer()
            optionsWidget = OptionPositions()
            optionsWidget.startTimer()
            window = MainWindow(stockWidget, optionsWidget)
            window.show()
    else:
        stockWidget = StockPositions()
        stockWidget.startTimer()
        optionsWidget = OptionPositions()
        optionsWidget.startTimer()
        window = MainWindow(stockWidget, optionsWidget)
        window.show()

    sys.exit(app.exec_())