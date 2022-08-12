import os
import sys
from tokenize import group
import webbrowser

import pylab
from PyQt5.QtWidgets import *
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice
from PyQt5 import uic
from ForUI import *
from PyQt5 import QtCore, QtGui, QtWidgets
# from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QPainter, QPen, QIcon
from PyQt5.QtCore import Qt,QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import webbrowser
from PyQt5.QtGui import QDesktopServices

import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

form_class = uic.loadUiType("design_main.ui")[0]
form_recom = uic.loadUiType("design_recom.ui")[0]

class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("LPOINT")
        self.if_cust = False
        self.if_history = False
        self.chnl_dv = 0
        # 버튼에 기능을 할당하는 코드
        self.lineEdit_cust_id.mousePressEvent = self._mousePressEvent
        self.lineEdit_cust_id.returnPressed.connect(self.printTextFunction)
        self.pushButton_cust_id.clicked.connect(self.changeTextFunction)
        self.pushButton_recom.clicked.connect(self.changeWindowFunction)
        self.connect = ForUI()

        # 창 이름, 로고 변경
        self.setWindowTitle('Lotte Recommend System')
        self.setWindowIcon(QIcon('icon_logo2.PNG'))

    def _mousePressEvent(self, event):
        self.lineEdit_cust_id.clear()
        # self.lineEdit_cust_id.mousePressEvent = None

    def Information_event(self):
        self.buttonReply = QMessageBox.information(
            self, '선호 채널 선택', "구매 이력이 없으시군요!\n온라인 구매를 선호하시면 Yes,오프라인 구매를 선호하시면 No를 클릭해주세요.", 
            QMessageBox.Yes | QMessageBox.No)

        if self.buttonReply == QMessageBox.Yes:
            self.chnl_dv = 2
            print('Online clicked.')
        elif self.buttonReply == QMessageBox.No:
            self.chnl_dv = 1
            print('Offline clicked.')

    def changeWindowFunction(self):
        if self.if_cust:
            if self.if_history:
                self.nw_recom = NewWindow(self.cust_id, self.if_history, None)
            else:
                self.Information_event()
                self.nw_recom = NewWindow(self.cust_id, self.if_history, self.chnl_dv)

        else:
            QMessageBox.information(self, '경고', '모든 정보를 입력해주세요.')

    def resetTextFunction(self):
        self.lineEdit_cust_id.clear()

    def printTextFunction(self):
        # 고객번호 -> 인적사항 출력
        self.cust_id = self.lineEdit_cust_id.text()
        # M035502859 - M263323245 -> 순서대로 구매이력O,구매이력X
        cust_info = self.connect.personal_info(self.cust_id)
        if cust_info:  # 고객O
            self.label_gender.setText(cust_info[0])
            self.label_age.setText(cust_info[1])
            self.label_zon.setText(cust_info[2])
            self.if_history = cust_info[3]
            self.if_cust = True
            self.piechart_chnl()
        else:  # 고객X
            QMessageBox.information(self, '경고', '고객 정보가 존재하지 않습니다.')
            self.label_gender.setText("")
            self.label_age.setText("")
            self.label_zon.setText("")
            self.resetTextFunction()

    def changeTextFunction(self):
        self.printTextFunction()

    def piechart_chnl(self):
        try:
            if self.verticalLayout_graph.count() > 0:
                self.verticalLayout_graph.itemAt(0).widget().setParent(None)
            self.fig = plt.Figure()
            self.canvas = FigureCanvas(self.fig)
            self.verticalLayout_graph.addWidget(self.canvas)
            colors = sns.color_palette('Paired')[0:2]
            tmp = self.connect.por_chnl(self.cust_id)
            ax = self.fig.add_subplot(111)
            ax.pie([s[1] for s in tmp],labels=[s[0] for s in tmp],labeldistance=1.2,colors=colors,wedgeprops = { 'linewidth' : 1.8, 'edgecolor' : 'white' },autopct='%.1f%%')
            self.canvas.draw()
        except Exception as e:
            QMessageBox.information(self, '경고', '구매이력이 없으시군요!')
            print(e, "main_design.py: piechart_chnl")
            return


class NewWindow(QWidget, form_recom):
    def __init__(self, cust_id, if_history, chnl_dv):
        super().__init__()
        self.connect = ForUI()
        self.cust_id = cust_id
        self.if_history = if_history
        self.chnl_dv = chnl_dv
        self.web = QWebEngineView()

        # 창 이름, 로고 변경
        self.setWindowTitle('Lotte Recommend System')
        self.setWindowIcon(QIcon('icon_logo2.PNG'))

        if self.if_history:
            self.arr = self.connect.recommendation_model(self.cust_id)
        else:
            self.arr = self.connect.for_no_history(self.cust_id, self.chnl_dv)
        self.setupUi(self)
        self.setWindowTitle("오늘의 추천 - " + self.title())
        self.show()
        self.set_recom()

    def title(self):
        if self.if_history:
            return '구매횟수:'+str(self.connect.my_history(self.cust_id))
        else:
            return '신규 사용자'

    def set_recom(self):
        layout = self.grid_prod
        for i in range(len(self.arr)):
            layout.addWidget(self.createLink(i), i // 3, i % 3)  ### TODO: [소현]외부 링크를 통해 사진 및 텍스트로 대체 예정
        self.setLayout(layout)

    def createLink(self,i):
        groupbox = QGroupBox(self.arr[i])
        self.arr[i] = self.arr[i].replace("/", "%2F")
        mylink = "\"https://www.lotteon.com/search/search/search.ecn?render=search&platform=pc&q=" + self.arr[i] + "&mallId=4\""
        mytext = '<a href=' + mylink + '>담기</a>'
        label_shop = QTextBrowser()
        label_shop.setText(mytext)
        label_shop.setOpenExternalLinks(True)
        vbox = QVBoxLayout()
        vbox.addWidget(label_shop)
        groupbox.setLayout(vbox)
        return groupbox


    class LinkWindow(QMainWindow):
        def __init__(self):
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()