import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import pybithumb
import pyupbit
import time
from PyQt5.QtGui import QColor
from upbitpy import Upbitpy

tickers = ["KRW-BTC","KRW-ETH","KRW-EOS","KRW-TRX","KRW-BCH","KRW-ADA", "KRW-LTC",
           'KRW-XLM', 'KRW-QTUM', 'KRW-BSV']
form_class = uic.loadUiType("view3.ui")[0]


class Worker(QThread):
    finished = pyqtSignal(dict)

    def run(self):
        while True:
            data = {}
            # 전체 데이터 불러옴
            #all_data = pyupbit.get_current_price(tickers)
            upbit = Upbitpy()
            all_info = upbit.get_ticker(tickers)

            # 단기 급등여부 판단
            candle_num = 3
            for ticker in all_info:
                candle_dict = upbit.get_minutes_candles(1, ticker['market'], count=3)

                last_two = candle_dict[-3]['candle_acc_trade_volume']
                last_one = candle_dict[-2]['candle_acc_trade_volume']
                last = candle_dict[-1]['candle_acc_trade_volume']


                if "KRW-BTC" == ticker['market']:
                    print('----거래량-----')
                    print('현재: ' + str(last))
                    print('1분전: ' + str(last_one))
                    print('2분전: ' + str(last_two))
                #min_value = 9e+20
                #for data in range( 1, candle_list-1) :
                #    if data['candle_acc_trade_volume'] < min_value:
                #        min_value = data['candle_acc_trade_volume']

                volume_rising = '-'
                if last > last_one*2 or (last > last_one*1.5 and last_two > last_two*1.5):
                    rising = '급증'

                cur_price = ticker['trade_price']
                volume = ticker['acc_trade_volume_24h']
                signed_change_rate = ticker['signed_change_rate']

                #print(ticker['market'])

                data[ticker['market']] = (cur_price,) +  (volume,) + (signed_change_rate,) + (volume_rising,)


            # 작업이 완료됐을때 이벤트 발생(emit)
            # data 변수가 바인딩하고 있는 딕셔너리 객체가 전송됨
            self.finished.emit(data)
            time.sleep(1)




class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('업비트 시세 조회기')
        self.worker = Worker()
        self.worker.finished.connect(self.update_table_widget)
        self.worker.start()

        # 1초마다 호출
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

            # 현재 상승장 여부를 읽어옴
            self.tableWidget.setItem(i, 0, QTableWidgetItem(ticker))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(infos[0])))

            #self.tableWidget.setItem(i, 3, QTableWidgetItem(str('%.4f' % float(infos[4]))))
            #self.tableWidget.setItem(i, 4, QTableWidgetItem(str(infos[5] + '%')))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(str('%.4f' % infos[1])))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(str('%.2f' % (infos[2]*100)+'%')))

            # 상승장이면 빨간색으로 넣어줌
            if infos[3] == "급증":
                self.tableWidget.item(i, 4).setBackground(QColor(255, 0, 0))


app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()