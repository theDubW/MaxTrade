from PySide2.QtCore import QUrl, Qt
from PySide2.QtGui import QIcon, QKeySequence, QPixmap
from PySide2.QtWidgets import QMainWindow, QAction, QLabel, QWidget, QHBoxLayout, QTabWidget
import TradingBots.robinhoodBot as r
# import Icons.rc_images as rc_images

class MainWindow(QMainWindow):
    def __init__(self, stock_info, option_info):
        QMainWindow.__init__(self)
        self.robinhood = r.Robinhood()

        self.setWindowTitle("MaxTrade")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))
        # self.setWindowState(Qt.WindowMaximized)
        self.resize(800, 800)
        # self.addDockWidget(Qt.TopRightSection, stock_info)
        # main
        main_widget = MainWidget(self, stock_info, option_info)
        # main_widget.setObjectName("mainWidget")
        self.setCentralWidget(main_widget)

        #menu bar
        self.menu = self.menuBar()

        #File Menu Bar
        self.file_menu = self.menu.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)


        self.settings_menu = self.menu.addMenu("Settings")
        logout = QAction("Logout",self)
        logout.triggered.connect(self.logout_close)
        self.settings_menu.addAction(logout)

        self.status = self.statusBar()
        self.status.showMessage("Welcome to MaxTrade")

        # geometry = QApplication.instance().desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 1.0, geometry.height() * 1.0)
        stylesheet = "Style/stylesheet.qss"
        with open(stylesheet, "r") as f:
            self.setStyleSheet(f.read())
        # self.setStyleSheet("background-color:#ffffff;")

        

    def logout_close(self):
        self.robinhood.logout()
        self.close()
class MainWidget(QWidget):
    def __init__(self, parent, stock_info, option_info):
        super(MainWidget, self).__init__(parent)
        self.layout = QHBoxLayout()
        
        self.tabs = QTabWidget()
        self.tabs.addTab(stock_info, "Stock Bot")
        self.tabs.addTab(option_info, "Option Bot")
        # self.tabs.setTabShape(QTabWidget.Rounded)

        # self.layout.addWidget(stock_info, 1)
        # self.layout.setAlignment(stock_info,)
        # self.layout.setContentsMargins()
        # self.layout.addSpacing()
        # self.layout.addWidget(option_info, 1)
        # self.layout.setAlignment(option_info, Qt.AlignCenter)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.setObjectName("mainWidget")
        # self.setStyleSheet("background-color:#f7fff9;")
