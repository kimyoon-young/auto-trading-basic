import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pybithumb

tickers = ["BTC" ,"EOS"]
form_class = uic.loadUiType("bull.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        #5초마다 호출
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.timeout)

    def timeout(self):
        for i, ticker in enumerate(tickers):
            item = QTableWidgetItem(ticker)
            self.tableWidget.setItem(i, 0, item)
            price, last_ma5, state = self.get_market_infos(ticker)
            #문자열을 QTableWidgetItem 객체에 변환후 넣어줘야함
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(price)))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str(last_ma5)))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(state))

    def get_market_infos(self, ticker):
        df = pybithumb.get_ohlcv(ticker)
        ma5 = df['close'].rolling(window=5).mean()
        # 전일 이동 편균
        last_ma5 = ma5[-2]
        price = pybithumb.get_current_price(ticker)

        state = None
        if price > last_ma5:
            state = "상승장"
        else:
            state = "하락장"

        return price, last_ma5, state

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()