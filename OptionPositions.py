from PySide2.QtCore import Qt, QAbstractTableModel, QAbstractItemModel, QModelIndex, QTimer, Signal, QRegExp, QSize
from PySide2.QtGui import QColor, QFont, QDoubleValidator, QRegExpValidator
from PySide2.QtWidgets import (QVBoxLayout, QGridLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QLabel, QLayout, QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QListView, QScrollArea, QAbstractItemView)
import optionsBot as o

class OptionPositionsTable(QAbstractTableModel):
    def __init__(self, positions=None):
        QAbstractTableModel.__init__(self)
        self.load_data(positions)
    def load_data(self, data):
        self.tickers = data.index
        self.strike_price = data['Strike Price']
        self.type = data['Type']
        self.exp_date = data['Expiration Date']
        self.quantity = data['Quantity']
        self.mark_price = data['Market Price']
        self.percent_change = data['Percent Change']
        self.column_count = 7
        self.row_count = len(data.index)
    def rowCount(self, parent=QModelIndex()):
        return self.row_count
    def columnCount(self, parent=QModelIndex()):
        return self.column_count
    def headerData(self, section, orientation, role):
        if(role!=Qt.DisplayRole):
            return None
        if orientation==Qt.Horizontal:
            return ("Ticker","Strike Price","Type","Expiration Date", "Quantity", "Market Price", "Percent Change")[section]
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
                return "{:0.2f}".format(self.strike_price[row])
            elif column==2:
                return self.type[row]
            elif column==3:
                return self.exp_date[row]
            elif column==4:
                return "{:0.2f}".format(self.quantity[row])
            elif column==5:
                return "{:0.2f}".format(self.mark_price[row])
            elif column==6:
                return "{:0.2f}".format(self.percent_change[row])
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
                self.strike_price[row] = value
            elif column==2:
                self.type[row] = value
            elif column==3:
                self.exp_date[row] = value
            elif column==4:
                self.quantity[row] = value
            elif column==5:
                self.mark_price[row] = value
            elif column==6:
                self.percent_change[row] = value
            return True
        return QAbstractTableModel.setData(self, index, value, role)
    def flags(self, index):
        original_flags = super(OptionPositionsTable, self).flags(index)
        return original_flags | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable
    def updateTable(self):
        for i in range(len(self.tickers)):
            n =  QAbstractItemModel.createIndex(self, i, 0, None)
            self.setData(n, self.tickers[i])
        for i in range(len(self.strike_price)):
            n =  QAbstractItemModel.createIndex(self, i, 1, None)
            self.setData(n, self.strike_price[i])
        for i in range(len(self.type)):
            n =  QAbstractItemModel.createIndex(self, i, 2, None)
            self.setData(n, self.type[i])
        for i in range(len(self.exp_date)):
            n =  QAbstractItemModel.createIndex(self, i, 3, None)
            self.setData(n, self.exp_date[i])
        for i in range(len(self.quantity)):
            n =  QAbstractItemModel.createIndex(self, i, 3, None)
            self.setData(n, self.quantity[i])
        for i in range(len(self.mark_price)):
            n =  QAbstractItemModel.createIndex(self, i, 3, None)
            self.setData(n, self.mark_price[i])
        for i in range(len(self.percent_change)):
            n =  QAbstractItemModel.createIndex(self, i, 3, None)
            self.setData(n, self.percent_change[i])
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
class OptionPositions(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.robinhood = o.OptionsBot()
        self.robinhood.updateOptionPositions()
        self.positions = OptionPositionsTable(self.robinhood.getOptionPositions())
        self.table_view = QTableView()
        self.table_view.setModel(self.positions)
        self.table_view.verticalHeader().setVisible(False)
        # self.table_view.adjustSize()
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.resizeColumnsToContents()
        width = 3
        for i in range(self.positions.columnCount()):
            width = width+self.table_view.columnWidth(i)
        print("OPTION WIDTH: "+str(width))
        self.table_view.setMinimumWidth(width)
        # self.table_view.setMaximumWidth(500)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        #Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)

        #Widget Layout
        self.main_layout = QGridLayout()
        # self.main_layout = QVBoxLayout()

        # Add Label
        self.table_label = QLabel("Option Positions")
        f = QFont()
        f.setBold(True)
        f.setPointSize(15)
        self.table_label.setFont(f)
        self.table_label.adjustSize()

        #Add Stop Loss Form
        self.position_editing = QListWidget()
        self.position_editing.setGeometry(50, 70, 100, 75)
        for i in self.positions.tickers:
            self.position_editing.addItem(QListWidgetItem(i))
        # self.position_editing.adjustSize()
        self.position_editing.setResizeMode(QListView.Fixed)
        self.confirm = QPushButton("Confirm") 

        #Stop Loss/Take Profit + Validator to float
        stopVal = QRegExpValidator(QRegExp("^-([0-9]{1,2}[0]?|100)+(\.[0-9]{0,2})?$"))
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
        self.robinhood.sold_option_signal[list].connect(self.soldPosition)
        
        #Add Output Box
        self.output_text = "Option Bot Output:\n\n"
        self.output_box = OutputBox()
        self.output_box.setText(self.output_text)
        self.output_box.setWidgetResizable(True)
        self.output_box.setFixedSize(200, 100)
        # self.output_box.setGeometry(300, 100, 300, 100)

        # self.main_layout.addWidget(self.table_label)
        # self.main_layout.addWidget(self.table_view)
        # self.main_layout.addWidget(self.form_widget)
        # self.main_layout.addWidget(self.output_box)
        # self.main_layout.setAlignment(self.table_label, Qt.AlignCenter)
        # self.main_layout.setAlignment(self.form_widget, Qt.AlignCenter)
        # self.main_layout.setAlignment(self.output_box, Qt.AlignCenter)
        # self.main_layout.closestAcceptableSize(self.table_view, QSize(100, 200))
        # self.main_layout.setAlignment(self.table_view, Qt.AlignCenter)
        # self.main_layout.SetMaximumSize
        self.main_layout.addWidget(self.table_label,1,0,1,0, Qt.AlignTrailing)
        self.main_layout.addWidget(self.table_view,2,1,1,1,Qt.AlignTrailing)
        self.main_layout.addWidget(self.form_widget,3,0,1,0,Qt.AlignTrailing)
        self.main_layout.addWidget(self.output_box,4,0,1,0,Qt.AlignTrailing)
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.main_layout.setAlignment(self.table_label, Qt.AlignCenter)
        self.main_layout.setAlignment(self.table_view, Qt.AlignHCenter)
        self.main_layout.setAlignment(self.form_widget, Qt.AlignCenter)
        self.main_layout.setAlignment(self.output_box, Qt.AlignCenter)
        #main layout
        self.setLayout(self.main_layout)
    def updateData(self):
        self.robinhood.updateOptions()
        self.positions.load_data(self.robinhood.getOptionPositions())
        self.positions.updateTable()
        # print("Updated Data")
        return None
    def startTimer(self):
        self.timer.start(10000)
    def soldPosition(self, soldInfo):
        self.output_text += ("SOLD {} SHARES OF {} AT ${} FOR A {}% {}".format(soldInfo[0], soldInfo[1], soldInfo[2], soldInfo[3], "LOSS" if soldInfo[3]<0 else "GAIN"))
        self.output_box.setText(self.output_text)
        #Deleting Ticker from available list
        match_items = self.position_editing.findItems(soldInfo[1], Qt.MatchExactly)
        for item in match_items:
            row = self.position_editing.row(item)
            self.position_editing.takeItem(row)
        
    def updateOutput(self):
        self.output_text += ("{}:\nStop Loss set: {}%; Take Profit Set: {}%\n\n".format(self.position_editing.currentItem().text(),self.stop_loss.text(), self.take_profit.text()))
        # self.robinhood.sellStockPosition(self.position_editing.currentItem().text(), 1, float(self.stop_loss.text()[1:]), float(self.take_profit.text()))
        self.output_box.setText(self.output_text)