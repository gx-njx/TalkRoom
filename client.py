import socket
import sys
import threading
import time

from PyQt5 import QtCore, QtWidgets

from DetecIP import DetecIP
from clientUI import Ui_Dialog as ClientUI


class TalkRoom(QtWidgets.QWidget):
    revSign = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.revThread = threading.Thread(target=self.rev, args=[])
        self.running = False
        self.ui = ClientUI()
        self.ui.setupUi(self)
        self.ui.SendButton.clicked.connect(self.send)
        self.ui.findipButton.clicked.connect(self.findip)
        self.ui.connectButton.clicked.connect(self.connect)
        self.revSign.connect(self.updateText)

    def send(self):
        text = self.ui.sendText.toPlainText()
        self.socket.send(text.encode("utf-8"))
        self.ui.sendText.clear()
        self.ui.sendText.setFocus()

    def findip(self):
        pthread = threading.Thread(target=self.setip, args=[])
        pthread.start()
        self.ui.labelconnect.setStyleSheet("color: rgb(0, 0, 255);")
        _translate = QtCore.QCoreApplication.translate
        self.ui.labelconnect.setText(_translate("Dialog", "正在寻找"))

    def setip(self):
        hostip = socket.gethostbyname(socket.gethostname())
        ipdetect = DetecIP(hostip)
        iplist = ipdetect.getip()
        for ip in iplist:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.settimeout(0.001)
            try:
                data = client.connect_ex((ip, 23333))
                if data == 0:
                    self.ui.ipText.setText(ip)
                    self.ui.labelconnect.setStyleSheet("color: rgb(255, 0, 0);")
                    _translate = QtCore.QCoreApplication.translate
                    self.ui.labelconnect.setText(_translate("Dialog", "未连接"))
                    client.close()
                    return
            except:
                print("class TalkRoom--setip--connect_ex--except")
            client.close()

    def connect(self):
        self.ui.labelconnect.setStyleSheet("color: rgb(0, 0, 255);")
        _translate = QtCore.QCoreApplication.translate
        self.ui.labelconnect.setText(_translate("Dialog", "连接中"))
        ip = self.ui.ipText.text()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 导入 socket 模块
        try:
            data = self.socket.connect_ex((ip, 23333))
            if data != 0:
                self.socket.close()
                self.ui.labelconnect.setStyleSheet("color: rgb(255, 0, 0);")
                self.ui.labelconnect.setText(_translate("Dialog", "连接失败"))
                return
            self.running = True
            self.revThread.setDaemon(True)
            self.revThread.start()
            self.ui.labelconnect.setStyleSheet("color: rgb(0, 255, 0);")
            self.ui.labelconnect.setText(_translate("Dialog", "已连接"))
        except:
            pass

    def rev(self):
        soc = self.socket
        running = self.running
        revSign = self.revSign
        while running:
            print('rev running')
            try:
                data = soc.recv(1024).decode("utf-8")
                if not data:
                    print('rev running out')
                    break
                revSign.emit(data)
            except:
                print('rev running out')
                break
            time.sleep(0.5)

    def updateText(self, data):
        print(data)
        self.ui.textBrowser.append(data)
        self.ui.textBrowser.moveCursor(self.ui.textBrowser.textCursor().End)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    easy = TalkRoom()
    easy.show()
    sys.exit(app.exec_())
