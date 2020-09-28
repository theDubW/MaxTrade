from PySide2.QtWidgets import QApplication, QPushButton, QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMainWindow, QAction
from PySide2.QtQuick import QQuickView
from PySide2.QtGui import QIcon, QKeySequence, QPixmap
from PySide2.QtCore import QUrl, Slot, Qt

#Custom Widget Imports

class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        
        self.inputLabel = QLabel("Enter Trade Info")
        self.stop_loss = QLineEdit("Stop loss %")
        self.take_profit = QLineEdit("Take profit %")
        self.confirm = QPushButton("Confirm") 
        
        layout = QVBoxLayout()
        layout.addWidget(self.inputLabel)
        layout.addWidget(self.stop_loss)
        layout.addWidget(self.take_profit)
        layout.addWidget(self.confirm)
        self.setLayout(layout)

        self.confirm.clicked.connect(self.confirmLossGain)
    def confirmLossGain(self):
        print("Stop Loss: {}\nTake Profit: {}".format(self.stop_loss.text(), self.take_profit.text()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = Form()
    main = MainWindow(form)
    main.show()

    with open("style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    sys.exit(app.exec_())

# @Slot()
# def confirmLossGain():
#     print("")



#button e.g.
# app = QApplication(sys.argv)
# execute_bot = QPushButton("Set stop loss and gain")
# execute_bot.clicked.connect(setLossGain)
# execute_bot.show()

#QML E.G.
# view = QQuickView()
# url = QUrl("bot.qml")
# view.setSource(url)
# view.setResizeMode(QQuickView.SizeRootObjectToView)
# view.show()
# app.exec_()