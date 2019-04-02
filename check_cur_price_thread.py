import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pybithumb
import time

tickers = ["BTC","ETH","EOS","TRX","BCH","ADA"]
form_class = uic.loadUiType("view.ui")[0]


# BTC 조회하는 클래스
class Worker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        while True:
            data = {}
            # 전체 데이터 불러옴
            all_data = pybithumb.get_current_price("ALL")
            for ticker, infos in all_data.items() :
                if ticker in tickers:
                    data[ticker] = self.get_market_infos(ticker) + (infos['units_traded'],) + (infos['24H_fluctate_rate'],)

            # 작업이 완료됐을때 이벤트 발생(emit)
            # data 변수가 바인딩하고 있는 딕셔너리 객체가 전송됨
            self.finished.emit(data)
            time.sleep(1)

    def get_market_infos(self, ticker):
        try:

            df = pybithumb.get_ohlcv(ticker)
            ma5 = df['close'].rolling(window=5).mean()
            ma20 = df['close'].rolling(window=20).mean()
            # 전일 이동 편균
            last_ma5 = ma5[-2]
            last_ma20 = ma20[-2]
            price = pybithumb.get_current_price(ticker)
            return price, last_ma5, last_ma20
        except:
            None, None, None

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('시세 조회기')
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()

        # 5초마다 호출
        timer = QTimer(self)
        timer.start(1000)
        timer.timeout.connect(self.timeout)
        # self.datetime = QDateTime.currentDateTime()
        # self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))

    def timeout(self):
        self.datetime = QDateTime.currentDateTime()
        self.statusBar().showMessage(self.datetime.toString(Qt.DefaultLocaleLongDate))


    # finished 라는 시그널이 발생하면 해당 메소드가 호출됨
    # data는 바인딩 된 key와 value를 가져옴.
    @pyqtSlot(dict)
    def update_table_widget(self,data):

        for ticker, infos in data.items():
            i = tickers.index(ticker)
            self.tableWidget.setItem(i, 0, QTableWidgetItem(ticker))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(infos[0])))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str('%.4f' % float(infos[3]))))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str(infos[4] + '%')))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(str('%.4f' % infos[1])))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(str('%.4f' % infos[2])))


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()