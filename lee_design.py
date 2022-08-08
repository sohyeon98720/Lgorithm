import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from ForUI import *

form_lee = uic.loadUiType("design_lee.ui")[0]

class lee_window(QMainWindow, form_lee) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.show()