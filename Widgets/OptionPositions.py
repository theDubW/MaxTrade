from PySide2.QtCore import Qt, QAbstractTableModel, QAbstractItemModel, QModelIndex, QTimer, Signal, QRegExp, QSize
from PySide2.QtGui import QColor, QFont, QDoubleValidator, QRegExpValidator
from PySide2.QtWidgets import (QVBoxLayout, QGridLayout, QFormLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QLabel, QLayout, QDialog, QLineEdit, QPushButton, QListWidget, QListWidgetItem, QListView, QScrollArea, QAbstractItemView, QComboBox)
import TradingBots.optionsBot as o

class OptionPositionsTable(QAbstractTableModel):
    def __init__(self, positions=None):
        QAbstractTableModel.__init__(self)
        self.load_data(positions)
    def load_data(self, data):
        self.tickers = data['Ticker']
        self.strike_price = data['Strike Price']
        self.type = data['Type']
        self.exp_date = data['Expiration Date']
        self.quantity = data['Quantity']
        self.mark_price = data['Market Price']
        self.profit = data['Profit']
        self.percent_change = data['Percent Change']
        self.option_id=data['id']
        self.column_count = 8
        self.row_count = len(data.index)
    def rowCount(self, parent=QModelIndex()):
        return self.row_count
    def columnCount(self, parent=QModelIndex()):
        return self.column_count
    def headerData(self, section, orientation, role):
        if(role!=Qt.DisplayRole):
            return None
        if orientation==Qt.Horizontal:
            return ("Ticker","Strike Price","Type","Expiration Date", "Quantity", "Market Price", "Profit", "Percent Change")[section]
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
                return "{:0.2f}".format(self.profit[row])
            elif column==7:
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
                self.profit[row] = value
            elif column==7:
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
            n =  QAbstractItemModel.createIndex(self, i, 4, None)
            self.setData(n, self.quantity[i])
        for i in range(len(self.mark_price)):
            n =  QAbstractItemModel.createIndex(self, i, 5, None)
            self.setData(n, self.mark_price[i])
        for i in range(len(self.profit)):
            n =  QAbstractItemModel.createIndex(self, i, 6, None)
            self.setData(n, self.profit[i])
        for i in range(len(self.percent_change)):
            n =  QAbstractItemModel.createIndex(self, i, 7, None)
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
        curPositions = self.robinhood.getOptionPositions()
        # print(curPositions)
        self.positions = OptionPositionsTable(curPositions)
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
        # print("OPTION WIDTH: "+str(width))
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

        #Quantity combo box
        self.quantity = QComboBox()
        if(len(self.positions.quantity)>0):
            for i in range(int(self.positions.quantity[0])):
                self.quantity.addItem(str(i+1))

        #Add Stop Loss Form
        self.position_editing = QComboBox()
        # self.position_editing.setGeometry(50, 70, 100, 75)
        if(len(self.positions.quantity)>0):
            for i in range(len(self.positions.tickers)):
                self.position_editing.addItem(str(self.positions.tickers[i])+" "+str(self.positions.strike_price[i])+" "+str(self.positions.type[i])+" "+str(self.positions.exp_date[i]))
        else:
            self.quantity.addItem("0")
        self.position_editing.currentIndexChanged.connect(self.changeQuantity)
            # self.position_editing = QListWidget()
            # # self.position_editing.setGeometry(50, 70, 100, 75)
            # for i in self.positions.tickers:
            #     self.position_editing.addItem(QListWidgetItem(i))
            # # self.position_editing.adjustSize()
            # self.position_editing.setResizeMode(QListView.Fixed)
        self.confirm = QPushButton("Submit Order")

        #Stop Loss/Take Profit + Validator to float
        stopVal = QRegExpValidator(QRegExp("^-([0-9]{1,2}[0]?|100)+(\.[0-9]{0,2})?$"))
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
        
        #Add Output Box
        self.output_text = "Option Bot Output:\n\n"
        self.output_box = OutputBox()
        self.output_box.setText(self.output_text)
        self.output_box.setWidgetResizable(True)
        self.output_box.setFixedSize(200, 100)
        #Add slot connection to output from options
        self.robinhood.output[str].connect(self.addOutput)

        self.form_widget = QWidget()
        # self.form_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.form_layout.addRow(QLabel("Contract"),self.position_editing)
        self.form_layout.addRow(QLabel("Quantity"),self.quantity)
        self.form_layout.addRow(QLabel("Stop Loss %"),self.stop_loss)
        self.form_layout.addRow(QLabel("Take Profit %"),self.take_profit)
        self.form_layout.addRow(self.confirm)
        self.confirm.clicked.connect(self.updateOutput)
        self.form_widget.setLayout(self.form_layout)
        #Add Slot connection to sold signal
        self.robinhood.sold_option_signal[list].connect(self.soldPosition)

        #Trading bot section
        self.bot_label = QLabel("Option Trading Bot")
        self.bot_label.setFont(f)
        self.bot_label.adjustSize()

        self.bot_widget = QWidget()
        self.bot_layout = QVBoxLayout()
        self.bot_layout.setSpacing(0)
        self.bot_widget.setLayout(self.bot_layout)
        # self.bot_layout.addWidget(self.bot_label, Qt.AlignTop)
        self.bot_layout.addWidget(self.form_widget, Qt.AlignTop)
        self.bot_layout.addWidget(self.output_box, Qt.AlignHCenter)
        self.bot_layout.setAlignment(Qt.AlignHCenter)

        #Current orders section
        self.curr_orders_title = QLabel("Current Orders")
        subtitle = QFont()
        subtitle.setPointSize(12)
        self.curr_orders_title.setFont(subtitle)
        self.curr_orders_title.setAlignment(Qt.AlignHCenter)
        self.bot_layout.addWidget(self.curr_orders_title, Qt.AlignHCenter)

        self.curr_orders = QGridLayout()
        self.updateOrders()

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
        self.main_layout.addWidget(self.table_label,1,0, Qt.AlignCenter)
        self.main_layout.addWidget(self.table_view,2,0,Qt.AlignHCenter)
        self.main_layout.addWidget(self.bot_label,1,1,Qt.AlignCenter)
        # self.main_layout.addWidget(self.output_box,4,0,1,0,Qt.AlignTrailing)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.addWidget(self.bot_widget,2,1,Qt.AlignTop)
        self.main_layout.setAlignment(self.table_view, Qt.AlignHCenter)
        self.main_layout.setAlignment(self.table_label, Qt.AlignHCenter)
        # self.main_layout.setAlignment(self.table_view, Qt.AlignHCenter)
        # self.main_layout.setAlignment(self.form_widget, Qt.AlignCenter)
        # self.main_layout.setAlignment(self.output_box, Qt.AlignCenter)
        #main layout
        self.setLayout(self.main_layout)
    def updateOrders(self):
        if self.curr_orders.count()>0:
            for i in reversed(range(self.curr_orders.rowCount())):
                for j in range(self.curr_orders.columnCount()):
                    # print("i:{}, j:{}".format(i,j))
                    widgetToRemove = self.curr_orders.itemAtPosition(i,j).widget()
                    # remove it from the layout list
                    self.curr_orders.removeWidget(widgetToRemove)
                    # remove it from the gui
                    widgetToRemove.deleteLater()
        self.curr_orders.update()
        temp_layout=QGridLayout()
        
        t_label=QLabel("Contract")
        order_font = QFont()
        order_font.setPointSize(10)
        t_label.setFont(order_font)
        q_label=QLabel("Quantity")
        q_label.setFont(order_font)
        sl_label=QLabel("Stop Loss %")
        sl_label.setFont(order_font)
        tp_label=QLabel("Take Profit %")
        tp_label.setFont(order_font)
        temp_layout.addWidget(t_label,0,0)
        temp_layout.addWidget(q_label,0,1)
        temp_layout.addWidget(sl_label,0,2)
        temp_layout.addWidget(tp_label,0,3)
        temp_layout.addWidget(QWidget(),0,4)
        
        # print("CUR_ORDERS INITIAL SIZE: "+str(self.curr_orders.count()))
        curr_orders = self.robinhood.getCurrOptionOrders()
        # print(print("CUR ORDERS: "+str(curr_orders)))
        i=1
        # self.row_num 
        # self.curr_order_ticker = ""
        for order in curr_orders:
            contract = curr_orders[order]["ticker"]+" "+curr_orders[order]["strike_price"]+" "+curr_orders[order]["full_type"]+" "+curr_orders[order]['type']+" "+curr_orders[order]["expiration_date"]
            temp_layout.addWidget(QLabel(str(contract)),i,0)
            temp_layout.addWidget(QLabel(str(curr_orders[order]["quantity"])),i,1)
            temp_layout.addWidget(QLabel(str(curr_orders[order]["sl_percent"])),i,2)
            temp_layout.addWidget(QLabel(str(curr_orders[order]["tp_percent"])),i,3)
            cancel_button = QPushButton("Cancel")
            
            # print("i: "+str(i))
            # self.curr_order_ticker=str(order)
            row_num=i
            ticker=str(order)+""
            cancel_button.released.connect(lambda x=ticker:self.orderCanceled(str(x)))
            temp_layout.addWidget(cancel_button,i,4)
            i+=1
        self.curr_orders.setParent(None)
        self.curr_orders = temp_layout
        self.bot_layout.addLayout(self.curr_orders)
        # print("CUR_ORDERS END SIZE: "+str(self.curr_orders.count()))
        self.curr_orders.update()
    def updateData(self):
        self.robinhood.updateOptions()
        self.positions.load_data(self.robinhood.getOptionPositions())
        self.positions.updateTable()
        # print("Updated Data")
        return None
    def changeQuantity(self, index):
        self.quantity.clear()
        for i in range(int(self.positions.quantity[index])):
            self.quantity.addItem(str(i+1))
    def startTimer(self):
        self.timer.start(10000)
    def soldPosition(self, soldInfo):
        didProfit = soldInfo[4]>=0
        self.output_text += ("SOLD {} CONTRACTS OF {} {} FOR ${} PER CONTRACT, FOR A {} OF {}, OR A {} OF {}%".format(soldInfo[0], soldInfo[1], soldInfo[2], soldInfo[3], "GAIN" if didProfit else "LOSS", "$"+str(soldInfo[4]) if didProfit else "-$"+str(-1*soldInfo[4]), "GAIN" if didProfit else "LOSS", soldInfo[5]))
        self.output_box.setText(self.output_text)
        #Deleting Ticker from available list
        # match_items = self.position_editing.findItems(soldInfo[1], Qt.MatchExactly)
        # for item in match_items:
        #     row = self.position_editing.row(item)
        #     self.position_editing.takeItem(row)
    def orderCanceled(self, ticker):
        print("order canceled for {} option".format(ticker))
        self.robinhood.cancelAllOptionOrders(ticker)
        self.output_text+="Canceled sell order for "+self.robinhood.getTickerByID(ticker)+"\n\n"
        self.robinhood.deleteOptionOrder(ticker)
        self.output_box.setText(self.output_text)
        self.updateOrders()
    #add text to output box
    def addOutput(self, text):
        self.output_text+=text+"\n\n"
        self.output_box.setText(self.output_text)
        
    def updateOutput(self):
        self.output_text += ("{}:\nStop Loss set: {}%; Take Profit Set: {}%\n\n".format(self.position_editing.currentText(),self.stop_loss.text(), self.take_profit.text()))
        # self.position_editing.currentItem().text()
        #TODO Fix selling for options
        # self.robinhood.tempSell(self.position_editing.currentText()[0:self.position_editing.currentText().find(" ")], int(self.quantity.currentText()), float(self.stop_loss.text()[1:]), float(self.take_profit.text()), self.positions.option_id[self.position_editing.currentIndex()])
        self.robinhood.sellOptionPosition(self.position_editing.currentText()[0:self.position_editing.currentText().find(" ")], int(self.quantity.currentText()), float(self.stop_loss.text()[1:]), float(self.take_profit.text()), self.positions.option_id[self.position_editing.currentIndex()])
        # self.robinhood.sellStockPosition(self.position_editing.currentItem().text(), 1, float(self.stop_loss.text()[1:]), float(self.take_profit.text()))
        self.output_box.setText(self.output_text)
        self.updateOrders()