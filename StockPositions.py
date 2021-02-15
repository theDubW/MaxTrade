from PySide2.QtCore import Qt, QAbstractTableModel, QAbstractItemModel, QModelIndex, QTimer, Signal, QRegExp
from PySide2.QtGui import QColor, QFont, QDoubleValidator, QRegExpValidator
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QLabel, QLayout, QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QListView, QScrollArea, QAbstractItemView, QComboBox)

import robinhoodBot as r
class StockPositionsTable(QAbstractTableModel):
    def __init__(self, positions=None):
        QAbstractTableModel.__init__(self)
        self.load_data(positions)
    def load_data(self, data):
        self.tickers = data.index
        self.quantity = data['Quantity']
        self.equity = data['Equity']
        self.pct_change = data['Percent Change']
        self.column_count = 4
        self.row_count = len(data.index)
    def rowCount(self, parent=QModelIndex()):
        return self.row_count
    def columnCount(self, parent=QModelIndex()):
        return self.column_count
    def headerData(self, section, orientation, role):
        if(role!=Qt.DisplayRole):
            return None
        if orientation==Qt.Horizontal:
            return ("Ticker","Quantity","Equity","Percent Change")[section]
        else:
            return "{}".format(section)
    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.DisplayRole:
            #Changing formats of cells (if necessary)
            if column==0:
                return self.tickers[row] 
            elif column==1:
                return "{:0.2f}".format(self.quantity[row])
            elif column==2:
                return "{:0.2f}".format(self.equity[row])
            elif column==3:
                return "{:0.2f}".format(self.pct_change[row])
        elif role==Qt.BackgroundRole:
            return QColor(Qt.white)
        elif role==Qt.TextAlignmentRole:
            return Qt.AlignRight
        return None
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            column = index.column()
            row = index.row()
            if column==0:
                return True
            elif column==1:
                self.quantity[row] = value
            elif column==2:
                self.equity[row] = value
            elif column==3:
                self.pct_change[row] = value
            return True
        return QAbstractTableModel.setData(self, index, value, role)
    def flags(self, index):
        original_flags = super(StockPositionsTable, self).flags(index)
        return original_flags | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
    def updateTable(self):
        for i in range(len(self.tickers)):
            n =  QAbstractItemModel.createIndex(self, i, 0, None)
            self.setData(n, self.tickers[i])
        for i in range(len(self.quantity)):
            n =  QAbstractItemModel.createIndex(self, i, 1, None)
            self.setData(n, self.quantity[i])
        for i in range(len(self.equity)):
            n =  QAbstractItemModel.createIndex(self, i, 2, None)
            self.setData(n, self.equity[i])
        for i in range(len(self.pct_change)):
            n =  QAbstractItemModel.createIndex(self, i, 3, None)
            self.setData(n, self.pct_change[i])

# class PositionSet(QDialog):
#     def __init__(self, parent=None):
#         super(PositionSet, self).__init__(parent)
#         self.position_number = QLineEdit("Position Number")
#         self.stop_loss = QLineEdit("Stop Loss %")
#         self.take_profit = QLineEdit("Take Profit %")
#         self.confirm = QPushButton("Confirm") 

#         layout = QVBoxLayout()
#         layout.addWidget(self.position_number)
#         layout.addWidget(self.stop_loss)
#         layout.addWidget(self.take_profit)
#         layout.addWidget(self.confirm)
#         self.setLayout(layout)
#         # self.confirm.clicked.connect(self.confirmLossGain)
#     def confirmLossGain(self):
#         print("Stop Loss: {}\nTake Profit: {}".format(self.stop_loss.text(), self.take_profit.text()))

class OutputBox(QScrollArea):
    def __init__(self):
        QScrollArea.__init__(self)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        layout = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        self.setStyleSheet("QWidget{background-color:white};")
        layout.addWidget(self.label)
    def setText(self, text):
        self.label.setText(text)
class StockPositions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.robinhood = r.Robinhood()
        self.robinhood.updateStockHoldings()
        self.positions = StockPositionsTable(self.robinhood.getStockHoldings())
        self.table_view = QTableView()
        self.table_view.setModel(self.positions)
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.adjustSize()

        self.table_view.resizeColumnsToContents()
        width = 3
        for i in range(self.positions.columnCount()):
            width = width+self.table_view.columnWidth(i)
        print("STOCK WIDTH: "+str(width))
        self.table_view.setMaximumWidth(width)
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.horizontal_header.setStretchLastSection(True)
        # self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.table_view.setMaximumWidth(500)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)


        #Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)


        #Headers n stuff

        # self.horizontal_header.setStretchLastSection(True)

        #Widget Layout
        self.main_layout = QGridLayout()
        # self.main_layout = QHBoxLayout()
        # self.main_layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.main_layout)

        # size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Add Label
        self.table_label = QLabel("Stock Positions")
        # self.table_label.setStyleSheet("border: 1px solid black;")
        # self.table_label.move(100,0)
        title = QFont()
        title.setBold(True)
        title.setPointSize(15)
        self.table_label.setFont(title)
        self.table_label.adjustSize()
        
        #Quantity combo box
        self.quantity = QComboBox()
        if(len(self.positions.quantity)>0):
            for i in range(int(self.positions.quantity[0])):
                self.quantity.addItem(str(i+1))
        else:
            self.quantity.addItem("0")
        #Add Stop Loss Form
        # self.position_number = QLineEdit("Position Number")
        self.position_editing = QComboBox()
        # self.position_editing.setGeometry(50, 70, 100, 75)
        for i in self.positions.tickers:
            self.position_editing.addItem(i)
        self.position_editing.currentIndexChanged.connect(self.changeQuantity)
        # self.position_editing.adjustSize()
        # self.position_editing.setResizeMode(QListView.Fixed)
        self.confirm = QPushButton("Submit Order") 

        #Stop Loss/Take Profit + Validator to float
        stopVal = QRegExpValidator(QRegExp("^-([0-9]{1,2}[0]?|100)+(\.[0-9]{0,2})?$"))
        # stopVal.setBottom(-100)
        # stopVal.setTop(0)
        # stopVal.setDecimals(2)
        # stopVal.setNotation(QDoubleValidator.StandardNotation)
        profitVal = QDoubleValidator()
        profitVal.setBottom(0)
        profitVal.setDecimals(2)
        profitVal.setNotation(QDoubleValidator.StandardNotation)
        self.stop_loss = QLineEdit()
        # self.stop_loss.setPlaceholderText("Stop Loss %")
        self.take_profit = QLineEdit()
        # self.take_profit.setPlaceholderText("Take Profit %")
        self.stop_loss.setValidator(stopVal)
        self.take_profit.setValidator(profitVal)

        self.bot_label = QLabel("Stock Trading Bot")
        self.bot_label.setFont(title)
        self.bot_label.adjustSize()
        # self.bot_label.setAlignment(Qt.AlignHCenter)

        #Add Output Box
        self.output_text = "Stock Bot Output:\n\n"
        self.output_box = OutputBox()
        self.output_box.setText(self.output_text)
        self.output_box.setWidgetResizable(True)
        self.output_box.setFixedSize(200, 100)
        # self.output_box.setAlignment(Qt.AlignTop)

        self.form_widget = QWidget()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("Ticker"),self.position_editing)
        self.form_layout.addRow(QLabel("Quantity"),self.quantity)
        self.form_layout.addRow(QLabel("Stop Loss %"),self.stop_loss)
        self.form_layout.addRow(QLabel("Take Profit %"),self.take_profit)
        self.form_layout.addRow(self.confirm)
        self.confirm.clicked.connect(self.updateOutput)
        self.form_widget.setLayout(self.form_layout)

        #Current orders section
        self.curr_orders_title = QLabel("Current Orders")
        subtitle = QFont()
        subtitle.setPointSize(12)
        self.curr_orders_title.setFont(subtitle)

        self.bot_widget = QWidget()
        self.bot_layout = QVBoxLayout()
        self.bot_layout.setSpacing(0)
        self.bot_widget.setLayout(self.bot_layout)
        # self.bot_layout.addWidget(self.bot_label, Qt.AlignTop)
        self.bot_layout.addWidget(self.form_widget, Qt.AlignTop)
        self.bot_layout.addWidget(self.output_box, Qt.AlignHCenter)
        self.bot_layout.addWidget(self.curr_orders_title, Qt.AlignHCenter)
        self.bot_layout.setAlignment(Qt.AlignHCenter)
        

        #Add Slot connection to sold signal
        self.robinhood.sold_stock_signal[list].connect(self.soldPosition)
        
        # self.output_box.setGeometry(300, 100, 300, 100)

        self.main_layout.addWidget(self.table_label,1,0,Qt.AlignCenter)
        self.main_layout.addWidget(self.table_view,2,0,Qt.AlignHCenter)
        self.main_layout.addWidget(self.bot_label, 1, 1, Qt.AlignCenter)
        # self.main_layout.addLayout(self.bot_layout)
        self.main_layout.addWidget(self.bot_widget,2,1,Qt.AlignTop)
        # self.main_layout.addWidget(QLabel("TESTING"),3,1, 1, 1)

        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setAlignment(self.table_view, Qt.AlignHCenter)
        self.main_layout.setAlignment(self.table_label, Qt.AlignHCenter)
        # self.main_layout.setAlignment(self.bot_widget, Qt.AlignTop)
        # self.main_layout.setAlignment(self.bot_label, Qt.AlignHCenter)
        # self.main_layout.setAlignment(self.output_box, Qt.AlignHCenter|Qt.AlignTop)
        #main layout
        
    def updateData(self):
        self.robinhood.updateStocks()
        self.positions.load_data(self.robinhood.getStockHoldings())
        self.positions.updateTable()
        # print("Updated Data")
        return None
    def changeQuantity(self, index):
        self.quantity.clear()
        for i in range(int(self.positions.quantity[index])):
            self.quantity.addItem(str(i+1))
        # print("TICKER CHANGED, TIME TO CHANGE QUANTITY")
    def startTimer(self):
        self.timer.start(10000)
    def soldPosition(self, soldInfo):
        self.output_text += ("SOLD {} SHARES OF {} AT ${} FOR A {}% {}".format(soldInfo[0], soldInfo[1], soldInfo[2], soldInfo[3], "LOSS" if soldInfo[3]<0 else "GAIN"))
        self.output_box.setText(self.output_text)
        #Deleting Ticker from available list
        # match_items = self.position_editing.findItems(soldInfo[1], Qt.MatchExactly)
        # for item in match_items:
        #     row = self.position_editing.row(item)
        #     self.position_editing.takeItem(row)
        
    def updateOutput(self):
        self.output_text += ("{}:\nStop Loss set: {}%; Take Profit Set: {}%\n\n".format(self.position_editing.currentText(),self.stop_loss.text(), self.take_profit.text()))
        self.robinhood.cancelAllStockOrders(self.position_editing.currentText())
        self.robinhood.sellStockPosition(self.position_editing.currentText(), int(self.quantity.currentText()), float(self.stop_loss.text()[1:]), float(self.take_profit.text()))
        self.output_box.setText(self.output_text)