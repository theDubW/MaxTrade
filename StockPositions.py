from PySide2.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide2.QtGui import QColor
from PySide2.QtWidgets import (QVBoxLayout, QHeaderView, QSizePolicy,
                               QTableView, QWidget, QLabel, QLayout)


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
class StockPositions(QWidget):
    def __init__(self, positions):
        QWidget.__init__(self)

        self.positions = StockPositionsTable(positions)
        self.table_view = QTableView()

        #Headers n stuff
        self.table_view.setModel(self.positions)
        self.horizontal_header = self.table_view.horizontalHeader()
        self.vertical_header = self.table_view.verticalHeader()
        self.horizontal_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.vertical_header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # self.horizontal_header.setStretchLastSection(True)

        #Widget Layout
        self.main_layout = QVBoxLayout()
        size = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        #Add Label
        # self.table_label = QLabel("Stock Positions")
        # self.table_label.setStyleSheet("border: 1px solid black;")
        # self.table_label.move(100,0)
        # self.table_label.adjustSize()

        #Left Layout
        size.setHorizontalStretch(1)
        self.table_view.setSizePolicy(size)
        # self.main_layout.addWidget(self.table_label)
        self.main_layout.addWidget(self.table_view)
        #main layout
        self.setLayout(self.main_layout)