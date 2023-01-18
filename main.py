import sys

#QT imports
from PySide2.QtWidgets import QApplication, QDockWidget, QDialog, QMainWindow
from PySide2.QtGui import QFont

import Widgets.login as l

#Custom Widgets
from Widgets.StockPositions import StockPositions
from Widgets.OptionPositions import OptionPositions
from Widgets.MainWindow import MainWindow

#Helper Module
import TradingBots.robinhoodBot as r

if __name__ == '__main__':
    robinhood = r.Robinhood()
    isLoggedIn = False
    isLoggedIn = robinhood.login()
    app = QApplication(sys.argv)
    
    if(isLoggedIn == False):
        login = l.Login()
        login.login()
        if(login.exec_()==QDialog.Accepted):
            robinhood.login()
            stockWidget = StockPositions()
            stockWidget.startTimer()
            optionsWidget = OptionPositions()
            optionsWidget.startTimer()
            window = MainWindow(stockWidget, optionsWidget)
            window.show()
        else:
            sys.exit(app.exec_())
    else:
        stockWidget = StockPositions()
        stockWidget.startTimer()
        optionsWidget = OptionPositions()
        optionsWidget.startTimer()
        window = MainWindow(stockWidget, optionsWidget)
        window.show()
        
    font = QFont("DM Sans")
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)
    sys.exit(app.exec_())