import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pybithumb
import time

tickers = ["BTC","ETH","EOS","TRX","BCH","ADA"]
form_class = uic.loadUiType("view.ui")[0]



class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #5초마다 호출
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.timeout)
        #self.datetime = QDateTime.currentDateTime()
        #self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))
    def timeout(self):
        for i, ticker in enumerate(tickers):
            item = QTableWidgetItem(ticker)
            self.tableWidget.setItem(i, 0, item)
            price, volume, last_ma5, last_ma20 = self.get_market_infos(ticker)
            #문자열을 QTableWidgetItem 객체에 변환 후 삽입
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(price)))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str(volume)))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(last_ma5)))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str(last_ma20)))
            self.datetime = QDateTime.currentDateTime()
            self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))


    def get_market_infos(self, ticker):
        df = pybithumb.get_ohlcv(ticker)
        ma5 = df['close'].rolling(window=5).mean()
        ma20 = df['close'].rolling(window=20).mean()
        volume = df['volume'][-1]
        # 전일 이동 편균
        last_ma5 = ma5[-2]
        last_ma20 = ma20[-2]
        price = pybithumb.get_current_price(ticker)

        #all_data = pybithumb.get_current_price("ALL")
        # for ticker, data in all.items()
        return price, volume, last_ma5, last_ma20

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()