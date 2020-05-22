from untitled import Ui_Dialog
import sys
import os
from eninge import baiduenigne
import traceback
from PyQt5.QtWidgets import QApplication,QMessageBox,QWidget,QPushButton
from PyQt5 import QtGui

class interface(QWidget,Ui_Dialog):
    def __init__(self):
        super(interface, self).__init__()
        self.setupUi(self)
        self.speech_url_list =[]
        self.af ="pcm"
        # self.buttonBox.setStyleSheet("background-image:url(1.jpg)")
        # try:
        #     self.resizeEvent()
        # except:
        #     print(traceback.format_exc())

    # def resizeEvent(self):
    #     palette = QtGui.QPalette()
    #     pix = QtGui.QPixmap("1.jpg")
    #     palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pix))
    #     self.setPalette(palette)

    def on_urlfinshed(self):
        self.textBrowser.clear()
        str = self.lineEdit.text()
        if str:
            self.speech_url_list.append(str)
        else:
            self.show_chines_messageBox("",str)

    def get_result(self):
        self.clear()
        eninge = baiduenigne(self.speech_url_list)
        eninge.creat_task(self.af)
        eninge.query_result()
        result = eninge.get_result()
        print(result)
        if result:
            self.textBrowser.insertPlainText(result[0])
        pass
    def get_url(self):
        pass
    def clear_url(self):
        self.lineEdit.clear()

    def clear(self):
        self.lineEdit.clear()
        self.textBrowser.clear()

    def get_ad(self,string):
        self.af = string

    def show_chines_messageBox(self,title,str):
        messageBox = QMessageBox()
        messageBox.setWindowTitle('错误')
        messageBox.setText('url不能为空')
        messageBox.addButton(QPushButton('确定'), QMessageBox.YesRole)
        messageBox.exec_()

if __name__ == '__main__':
    # application 对象
    app = QApplication(sys.argv)
    # 这是qt designer实现的Ui_MainWindow类
    mainwindow = interface()
    palette = QtGui.QPalette()
    pix = QtGui.QPixmap("2.jpg")
    palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pix))
    mainwindow.setPalette(palette)
    # 显示
    mainwindow.show()

    sys.exit(app.exec_())
    os.system('pause')