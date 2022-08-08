import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from ForUI import *
import time

form_kimryu = uic.loadUiType("design_kimryu.ui")[0]

class kimryu_window(QMainWindow, form_kimryu) : # 연결은 했으나 Form이 잘 안나옴
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()
        time.sleep(3)
        self.close()