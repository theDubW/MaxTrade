from PySide2.QtCore import Qt, QAbstractTableModel, QAbstractItemModel, QModelIndex, QTimer, Signal, QRegExp
from PySide2.QtGui import QColor, QFont, QDoubleValidator, QRegExpValidator
from PySide2.QtWidgets import (QVBoxLayout, QGridLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QLabel, QLayout, QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QListView, QScrollArea)

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

class PositionSet(QDialog):
    def __init__(self, parent=None):
        super(PositionSet, self).__init__(parent)
        self.position_number = QLineEdit("Position Number")
        self.stop_loss = QLineEdit("Stop Loss %")
        self.take_profit = QLineEdit("Take Profit %")
        self.confirm = QPushButton("Confirm") 

        layout = QVBoxLayout()
        layout.addWidget(self.position_number)
        layout.addWidget(self.stop_loss)
        layout.addWidget(self.take_profit)
        layout.addWidget(self.confirm)
        self.setLayout(layout)
        # self.confirm.clicked.connect(self.confirmLossGain)
    def confirmLossGain(self):
        print("Stop Loss: {}\nTake Profit: {}".format(self.stop_loss.text(), self.take_profit.text()))

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
        self.robinhood.updateHoldings()
        self.positions = StockPositionsTable(self.robinhood.getStockHoldings())
        self.table_view = QTableView()

        #Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)


        #Headers n stuff
        self.table_view.setModel(self.positions)
        self.table_view.adjustSize()
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.horizontal_header.setStretchLastSection(True)

        #Widget Layout
        self.main_layout = QGridLayout()
        # size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Add Label
        self.table_label = QLabel("Stock Positions")
        # self.table_label.setStyleSheet("border: 1px solid black;")
        # self.table_label.move(100,0)
        f = QFont()
        f.setBold(True)
        f.setPointSize(15)
        self.table_label.setFont(f)
        self.table_label.adjustSize()

        #Add Stop Loss Form
        # self.position_number = QLineEdit("Position Number")
        self.position_editing = QListWidget()
        self.position_editing.setGeometry(50, 70, 100, 75)
        for i in self.positions.tickers:
            self.position_editing.addItem(QListWidgetItem(i))
        # self.position_editing.adjustSize()
        self.position_editing.setResizeMode(QListView.Fixed)
        self.confirm = QPushButton("Confirm") 

        #Stop Loss/Take Profit + Validator to float
        stopVal = QRegExpValidator(QRegExp("^-([1-9]{1,2}[0]?|100)+(\.[0-9]{0,2})?$"))
        # stopVal.setBottom(-100)
        # stopVal.setTop(0)
        # stopVal.setDecimals(2)
        # stopVal.setNotation(QDoubleValidator.StandardNotation)
        profitVal = QDoubleValidator()
        profitVal.setBottom(0)
        profitVal.setDecimals(2)
        profitVal.setNotation(QDoubleValidator.StandardNotation)
        self.stop_loss = QLineEdit()
        self.stop_loss.setPlaceholderText("Stop Loss %")
        self.take_profit = QLineEdit()
        self.take_profit.setPlaceholderText("Take Profit %")
        self.stop_loss.setValidator(stopVal)
        self.take_profit.setValidator(profitVal)
        

        self.form_widget = QWidget()
        self.form_layout = QVBoxLayout()
        self.form_layout.addWidget(self.position_editing)
        self.form_layout.addWidget(self.stop_loss)
        self.form_layout.addWidget(self.take_profit)
        self.form_layout.addWidget(self.confirm)
        self.confirm.clicked.connect(self.updateOutput)
        self.form_widget.setLayout(self.form_layout)

        #Add Slot connection to sold signal
        self.robinhood.sold_stock_signal.connect(self.soldPosition)
        
        #Add Output Box
        self.output_text = "Bot Output:\n\n"
        self.output_box = OutputBox()
        self.output_box.setText(self.output_text)
        self.output_box.setWidgetResizable(True)
        self.output_box.setFixedSize(200, 100)
        # self.output_box.setGeometry(300, 100, 300, 100)

        self.main_layout.addWidget(self.table_label,1,0,1,0, Qt.AlignTrailing)
        self.main_layout.addWidget(self.table_view,2,0,1,0,Qt.AlignTrailing)
        self.main_layout.addWidget(self.form_widget,3,0,1,0,Qt.AlignTrailing)
        self.main_layout.addWidget(self.output_box,4,0,1,0,Qt.AlignTrailing)
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.setAlignment(self.table_label, Qt.AlignCenter)
        self.main_layout.setAlignment(self.form_widget, Qt.AlignCenter)
        self.main_layout.setAlignment(self.output_box, Qt.AlignCenter)
        #main layout
        self.setLayout(self.main_layout)
    def updateData(self):
        self.robinhood.update()
        self.positions.load_data(self.robinhood.getStockHoldings())
        self.positions.updateTable()
        # print("Updated Data")
        return None
    def startTimer(self):
        self.timer.start(10000)
    def soldPosition(self):
        self.output_text += ("SOLD POSITION")
        self.output_box.setText(self.output_text)
    def updateOutput(self):
        self.output_text += ("{}:\nStop Loss set: {}%; Take Profit Set: {}%\n\n".format(self.position_editing.currentItem().text(),self.stop_loss.text(), self.take_profit.text()))
        self.robinhood.sellStockPosition(self.position_editing.currentItem().text(), 0, float(self.stop_loss.text()), float(self.take_profit.text()))
        self.output_box.setText(self.output_text)