import sys
from PyQt5.QtWidgets import *


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(500,200,300,400)
        self.setWindowTitle("PyQt")

        #display on Mywindow
        btn = QPushButton("버튼1", self)

app = QApplication(sys.argv)
window = MyWindow()
window.show()
app.exec_()