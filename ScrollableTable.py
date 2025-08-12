from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
MAX_ROWS = 86400*2

class ScrollableTable(QWidget):
    def __init__(self, rows: int, columns: int, headers: list = None, data: list = None, min_width = 50):
        """
        可捲動表格
        :param rows: 列數
        :param columns: 欄數
        :param headers: 欄位標題 (list)
        :param data: 資料 (list of lists)
        """
        super().__init__()
        self.layout = QVBoxLayout(self)

        # 建立 QTableWidget
        self.table = QTableWidget(rows, columns)
        self.layout.addWidget(self.table)
        self.headers = headers
        self.initInstance = None

        # 設定表頭
        if headers:
            self.table.setHorizontalHeaderLabels(headers)

        # 如果有資料就填入
        if data:
            self.set_data(data)

        # 調整欄寬自動填滿
        self.set_table_Stretch()

        # 預設可捲動
        self.table.setVerticalScrollBarPolicy(2)   # Always On
        self.table.setHorizontalScrollBarPolicy(2) # Always On

    def set_data(self, data: list):
        """填入資料"""
        for row_idx, row_data in enumerate(data):
            for col_idx, value in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

    def set_init(self, row_data, resize = True):
        self.initInstance = (row_data, resize)
        self.add_row_to_top(self.initInstance[0], self.initInstance[1])

    def add_row_to_top(self, row_data, resize = True):
        """在最上方插入新資料"""
        if resize and self.Stretch:
            self.set_table_ResizeToContents()

        self.table.insertRow(0)  # 在第 0 列插入新行
        for col, value in enumerate(row_data):
            self.table.setItem(0, col, QTableWidgetItem(str(value)))
        # 如果超過最大行數，刪除最後一列
        if self.table.rowCount() > MAX_ROWS:
            self.table.removeRow(self.table.rowCount() - 1)

    def get_data(self):
        data = []
        row_count = self.table.rowCount()
        col_count = self.table.columnCount()

        for row in range(row_count):
            row_data = []
            for col in range(col_count):
                item = self.table.item(row, col)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append("")  # 如果該格是空的就放空字串
            data.append(row_data)
        return data
    
    def set_table_Stretch(self):
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Stretch = True

    def set_table_ResizeToContents(self):
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.Stretch = False

    def clear(self):
        self.table.clear()
        if self.headers:
            self.table.setHorizontalHeaderLabels(self.headers)
        if self.initInstance:
            self.add_row_to_top(self.initInstance[0], self.initInstance[1])