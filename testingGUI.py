from PySide2.QtWidgets import QApplication, QPushButton
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl, Slot

import sys

@Slot()
def setLossGain():
    print("Set the stop loss and take profit!")

app = QApplication(sys.argv)

execute_bot = QPushButton("Set stop loss and gain")
execute_bot.clicked.connect(setLossGain)
execute_bot.show()

#QML E.G.
# view = QQuickView()
# url = QUrl("bot.qml")


# view.setSource(url)
# view.setResizeMode(QQuickView.SizeRootObjectToView)
# view.show()
app.exec_()