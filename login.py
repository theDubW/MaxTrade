from PySide2.QtWidgets import QLineEdit, QPushButton, QVBoxLayout, QDialog, QMessageBox, QMainWindow, QApplication
from PySide2.QtGui import QIcon, QPixmap
# from mainwindow import Ui_MainWindow
import robinhoodBot as r
import robin_stocks.helper as helper
import robin_stocks.authentication as auth
import robin_stocks.urls as urls
#Verification Code
class vCode(QDialog):
    def __init__(self, parent=None):
        super(vCode, self).__init__(parent)
        self.code = QLineEdit(self)
        self.code.setPlaceholderText("SMS Verification Code")
        self.buttonConfirm = QPushButton('Confirm', self)
        self.buttonConfirm.clicked.connect(self.handleCode)
        layout = QVBoxLayout(self)
        layout.addWidget(self.code)
        layout.addWidget(self.buttonConfirm)
    def handleCode(self):
        # auth.respond_to_challenge(urls.challenge_url)
        return False
class Login(QDialog):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.robinhood = r.Robinhood()

        self.textName = QLineEdit(self)
        self.textName.setPlaceholderText("Robinhood Username/Email")
        self.textPass = QLineEdit(self)
        self.textPass.setPlaceholderText("Robinhood Password")
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.setWindowTitle("MaxTrade Login")
        self.setWindowIcon(QIcon(QPixmap(":/Icons/logo.png")))
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        self.robinhood.setUsernamePW(self.textName.text(), self.textPass.text())
        try:
            if(self.robinhood.login()):
                self.accept()
        except Exception as e:
            print(e)
            QMessageBox.warning(
                self, 'Error', 'Incorrect username or password')
        else:
            authCode = vCode()
            if(authCode.exec_() == QDialog.Accepted):
                self.accept()