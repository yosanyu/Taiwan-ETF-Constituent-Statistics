import etfloader
import requester
import stockloader
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QMainWindow, QApplication, QTableWidget, QLabel, QPushButton, QComboBox, QMessageBox, QPlainTextEdit
)


class WorkerThread(QThread):
    result_ready = Signal(str)

    def __init__(self, etf_requester, parent=None):
        self.etf_requester = etf_requester
        super().__init__(parent)

    def run(self):
        # 綁定回調函數
        self.etf_requester.callback_text = self.callback
        self.etf_requester.start_request()

    def callback(self, text):
        self.result_ready.emit(text)


class MainWindow(QMainWindow):
    def __init__(self):
        self.etf_loader = etfloader.ETFLoader()
        self.stock_loader = stockloader.StockLoader()
        self.etfs = []
        self.plain_text = ''
        self.table = None
        self.button_add = None
        self.button_confirm = None
        self.button_clear = None
        self.combobox_etf_issuer = None
        self.combobox_etf_title = None
        self.plain_text_edit = None
        self.worker_thread = None
        self.window_setting()
        self.init_widget()

    def window_setting(self):
        super(MainWindow, self).__init__()
        self.resize(1600, 900)
        self.setFixedSize(1600, 900)
        self.setWindowTitle("Constituent Statistics")

    def init_widget(self):
        self.init_button()
        self.init_combobox()
        self.init_plain_text_edit()

    def init_button(self):
        self.button_add = QPushButton(self)
        self.button_confirm = QPushButton(self)
        self.button_clear = QPushButton(self)
        self.button_add.setGeometry(1200, 50, 100, 50)
        self.button_confirm.setGeometry(1320, 50, 100, 50)
        self.button_clear.setGeometry(1440, 50, 100, 50)
        self.button_add.setText("新增")
        self.button_confirm.setText("確認")
        self.button_clear.setText("重置")
        font = self.button_add.font()
        font.setPointSize(20)
        self.button_add.setFont(font)
        self.button_confirm.setFont(font)
        self.button_clear.setFont(font)
        self.button_add.clicked.connect(self.on_button_add_clicked)
        self.button_confirm.clicked.connect(self.on_button_confirm_clicked)
        self.button_clear.clicked.connect(self.on_button_clear_clicked)

    def init_combobox(self):
        self.combobox_etf_issuer = QComboBox(self)
        self.combobox_etf_title = QComboBox(self)
        self.combobox_etf_issuer.setGeometry(50, 50, 250, 50)
        self.combobox_etf_title.setGeometry(350, 50, 800, 50)
        self.combobox_etf_issuer.addItems(self.etf_loader.etf_issuer)
        self.combobox_etf_title.addItems(self.etf_loader.get_title(0))
        font = self.combobox_etf_issuer.font()
        font.setPointSize(20)
        self.combobox_etf_issuer.setFont(font)
        self.combobox_etf_title.setFont(font)
        self.combobox_etf_issuer.currentIndexChanged.connect(self.etf_issuer_changed)

    def init_plain_text_edit(self):
        self.plain_text_edit = QPlainTextEdit(self)
        self.plain_text_edit.setGeometry(100, 200, 1400, 600)
        font = self.plain_text_edit.font()
        font.setPointSize(30)
        self.plain_text_edit.setFont(font)
        self.update_plain_text()
        self.plain_text_edit.show()

    def on_button_add_clicked(self):
        etf_issuer_index = self.combobox_etf_issuer.currentIndex()
        etf_code_index = self.combobox_etf_title.currentIndex()
        etf_code = self.etf_loader.etf_code[etf_issuer_index][etf_code_index]
        if etf_code not in self.etfs:
            self.etfs.append(etf_code)
            message = '已新增{}進入統計\n'.format(etf_code)
            self.add_plain_text(message)

    def on_button_confirm_clicked(self):
        if len(self.etfs) > 0:
            etf_requester = requester.ETFRequester(self.etfs)
            # 綁定回調函數
            etf_requester.callback_get_stock = self.get_stock_name
            # 建立QT Thread
            self.worker_thread = WorkerThread(etf_requester)
            self.worker_thread.result_ready.connect(self.add_plain_text)
            self.worker_thread.start()

    def on_button_clear_clicked(self):
        self.etfs = []
        self.clear_plain_text()

    def etf_issuer_changed(self, index):
        self.combobox_etf_title.clear()
        self.combobox_etf_title.addItems(self.etf_loader.get_title(index))

    def add_plain_text(self, text):
        self.plain_text += text
        self.update_plain_text()

    def clear_plain_text(self):
        self.plain_text = ''
        self.update_plain_text()

    def update_plain_text(self):
        self.plain_text_edit.setPlainText(self.plain_text)
        scrollbar = self.plain_text_edit.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def get_stock_name(self, key):
        return self.stock_loader.get_stock_name(key)