import os
import sys

import pylab
from PyQt5.QtWidgets import *
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5 import uic
from ForUI import *
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
            QMessageBox.information(self, '경고', '회원번호먼저 입력해주세요.')

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
            if cust_info:
                hs = "있음"
            else:
                hs = "없음"
            self.label_cust_num.setText(hs)
            self.if_history = cust_info[3]
            self.if_cust = True
        else: # 고객X
            QMessageBox.information(self, '경고', '고객 정보가 존재하지 않습니다.')
            self.label_gender.setText("")
            self.label_age.setText("")
            self.label_zon.setText("")
            self.label_cust_num.setText("")
            self.resetTextFunction()

    def changeTextFunction(self) :
        self.printTextFunction()
    
    def piechart_count(self):
        # M223630342
        ###TODO: [승건]새로운 창에 만드는거말고 기존 창에 표시하기
        if self.if_cust and self.if_history:
            tmp = self.connect.por_count(self.cust_id)
            series = QPieSeries()
            for i,j in tmp :
                series.append(i,j)
            series.setLabelsVisible(True)
        elif self.if_cust:
            QMessageBox.information(self, '경고', '구매이력이 없으시군요!')
        else:
            QMessageBox.information(self, '경고', '회원번호먼저 입력해주세요.')
        try:
            series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
            for slice in series.slices():
                if 100 * slice.percentage() >= 10: # 비중이 적은건 잘 안보여서 1. 화살표 후 따로 빼기 2. 보이지않게하기 중 2번 선택
                    slice.setLabel("{:.2f}%".format(100 * slice.percentage()))

            chart = QChart()
            chart.setTitle(self.cust_id+"님의 카테고리별 구매이력입니다")
            chart.addSeries(series)
            chart.createDefaultAxes()
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            for i in range(5):
                chart.legend().markers(series)[i].setLabel(tmp[i][0])
            chartview = QChartView(chart)
            chartview.setRenderHint(QPainter.Antialiasing)
            ###TODO: [지혜] 폰트 크기나 색 등 수정
            self.setCentralWidget(chartview)
        
        except Exception as e:
            print(e, "main_design.py: piechart_count")
            return
    
    def piechart_price(self):
        if self.if_cust and self.if_history:
            tmp = self.connect.por_price(self.cust_id)
            series = QPieSeries()
            for i,j in tmp :
                series.append(i,j)
            series.setLabelsVisible(True)
        elif self.if_cust:
            QMessageBox.information(self, '경고', '구매이력이 없으시군요!')
        else:
            QMessageBox.information(self, '경고', '회원번호먼저 입력해주세요.')
        try:
            series.setLabelsPosition(QPieSlice.LabelInsideHorizontal)
            for slice in series.slices():
                if 100 * slice.percentage() >= 10:
                    slice.setLabel("{:.2f}%".format(100 * slice.percentage()))

            chart = QChart()
            chart.setTitle(self.cust_id+"님의 카테고리별 구매이력입니다")
            chart.addSeries(series)
            chart.createDefaultAxes()
            chart.setAnimationOptions(QChart.SeriesAnimations)
            chart.legend().setVisible(True)
            chart.legend().setAlignment(Qt.AlignBottom)
            
            for i in range(5):
                chart.legend().markers(series)[i].setLabel(tmp[i][0])
            chartview = QChartView(chart)
            chartview.setRenderHint(QPainter.Antialiasing)
            ###TODO: [지혜] 폰트 크기나 색 등 수정
            self.setCentralWidget(chartview)
        
        except Exception as e:
            print(e, "main_design.py: piechart_count")
            return

class NewWindow(QWidget,form_recom):
    def __init__(self,cust_id,if_history):
        super().__init__()
        self.connect = ForUI()
        self.cust_id = cust_id
        self.if_history = if_history
        if self.if_history:
            self.arr = self.connect.most_common(self.cust_id)
            arr2 = self.connect.ncf(self.cust_id)
            self.arr.extend(arr2)
        else:
            self.arr = self.connect.for_no_history(self.cust_id)
        self.lower_bound = self.connect.if_lower_bound
        self.setupUi(self)
        self.setWindowTitle("LPOINT")
        self.show() ###TODO: 승건씨꺼 실행이 느려서 cust_id들어오는 순간부터 계산하고있는걸로 바꿀까 생각중 내가 함(지혜)
        self.set_recom()

    def set_recom(self):
        layout = self.grid_prod
        if self.if_history: #소현-지혜(일단 소현만 진행)
            ###TODO: [지혜] 추천 알고리즘 넣을 때 비율 정해서 넣기
            self.cust_cnt.setText('N회')  # 수정해야됨ㅋ

        else: # 승건
            self.cust_cnt.setText('0회')

        for i in range(len(self.arr)):
            label = QLabel(self.arr[i])
            label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(label,i//3,i%3) ### TODO: [소현]외부 링크를 통해 사진 및 텍스트로 대체 예정
        self.setLayout(layout)


if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()