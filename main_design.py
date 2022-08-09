import sys
from PyQt5.QtWidgets import *
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5 import uic
from ForUI import *
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt
import numpy as np
###TODO: [지혜] 기본적인 디자인 부탁

form_class = uic.loadUiType("design_main.ui")[0]
form_recom = uic.loadUiType("design_recom.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("LPOINT")
        self.if_cust = False
        self.if_history = False # False면 이승건, True면 소현-지혜
        #버튼에 기능을 할당하는 코드
        self.lineEdit_cust_id.mousePressEvent = self._mousePressEvent
        self.lineEdit_cust_id.returnPressed.connect(self.printTextFunction)
        self.pushButton_cust_id.clicked.connect(self.changeTextFunction)
        self.pushButton_recom.clicked.connect(self.changeWindowFunction)
        self.radioButton_count.clicked.connect(self.piechart_count)
        self.radioButton_price.clicked.connect(self.piechart_price)
        self.connect = ForUI()

    def _mousePressEvent(self, event):
        self.lineEdit_cust_id.clear()
        # self.lineEdit_cust_id.mousePressEvent = None

    def changeWindowFunction(self): ### TODO: [승건]창 하나만 띄워졌으면 좋겠음
        if self.if_cust:
            self.nw_recom = NewWindow(self.cust_id,self.if_history)
            # self.hide()
            # self.nw_recom.show()
            # if self.nw_recom.close():
            #     self.show()
        else:
            pass
            # print("회원번호먼저 입력해주세요!") ###TODO: [승건]오류메세지로 바꾸기

    def resetTextFunction(self):
        self.lineEdit_cust_id.clear()

    def printTextFunction(self) :
        # 고객번호 -> 인적사항 출력
        self.cust_id = self.lineEdit_cust_id.text()
        # M035502859 - M263323245 -> 순서대로 구매이력O,구매이력X
        cust_info = self.connect.personal_info(self.cust_id)
        if cust_info: # 고객O
            self.label_gender.setText(cust_info[0])
            self.label_age.setText(cust_info[1])
            self.label_zon.setText(cust_info[2])
            self.if_history = cust_info[3]
            self.if_cust = True
        else: # 고객X
            self.label_gender.setText("")
            self.label_age.setText("올바른 고객번호를\n입력해주세요!")
            self.label_zon.setText("")
            self.resetTextFunction()
            ###TODO: [승건] setText대신 오류메세지로 바꿨으면 좋겠음

    def changeTextFunction(self) :
        self.printTextFunction()
    
    def piechart_count(self):
        ###TODO: [승건]새로운 창에 만드는거말고 기존 창에 표시하기
        ###TODO: [승건]차트에 비율 표시
        if self.if_cust:
            tmp = self.connect.por_count(self.cust_id)
            self.series = QPieSeries()
            for i,j in tmp:
                self.series.append(i,j)
        else:
            ###TODO: [승건] 오류메세지: 회원번호 먼저 입력해주세요!
            pass
        self.slice = self.series.slices()[0]
        chart = QChart()
        chart.legend().hide()
        chart.addSeries(self.series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(self.cust_id+"님의 카테고리별 구매이력입니다")

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        self.setCentralWidget(chartview)
    
    def piechart_price(self):
        ###TODO: [소현] 만들기
        pass
            

class NewWindow(QWidget,form_recom):
    def __init__(self,cust_id,if_history):
        super().__init__()
        self.connect = ForUI()
        self.cust_id = cust_id
        self.if_history = if_history
        self.lower_bound = self.connect.if_lower_bound
        self.setupUi(self)
        self.setWindowTitle("LPOINT")
        self.show() ###TODO: 실행이 느려서 cust_id들어오면 미리 추천 계산해놓고 new window에서는 띄우기만 하는게 좋을듯
        self.set_recom()

    def set_recom(self):
        layout = self.grid_prod
        if self.if_history: #소현-지혜(일단 소현만 진행)
            ###TODO: [지혜] 추천 알고리즘 넣을 때 비율 정해서 넣기
            arr = self.connect.most_common(self.cust_id)
        else: # 승건
            arr = self.connect.for_no_history(self.cust_id)
        for i in range(len(arr)):
            label = QLabel(arr[i])
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label,i//3,i%3) ### TODO: [소현]외부 링크를 통해 사진 및 텍스트로 대체 예정
        self.setLayout(layout)


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()