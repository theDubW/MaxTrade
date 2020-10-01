from PySide2.QtCore import QUrl, Qt
from PySide2.QtGui import QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import QMainWindow, QAction, QLabel

import rc_images

class MainWindow(QMainWindow):
    def __init__(self, stock_info):
        QMainWindow.__init__(self)
        self.setWindowTitle("MaxTrade")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))
        self.setWindowState(Qt.WindowMaximized)
        # self.addDockWidget(Qt.TopRightSection, stock_info)
        self.setCentralWidget(stock_info)

        self.menu = self.menuBar()
        self.file_menu = self.menu.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

        self.file_menu.addAction(exit_action)

        self.status = self.statusBar()
        self.status.showMessage("Welcome to MaxTrade")

        # geometry = QApplication.instance().desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 1.0, geometry.height() * 1.0)
