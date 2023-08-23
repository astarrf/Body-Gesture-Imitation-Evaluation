from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtGui, QtCore
import sys
from dance import Ui_MainWindow
from threading import Thread, Event
import qimage2ndarray
import time
import VideoMain
import cv2

# 导入PyQt5和其他必要的模块

# 用于在主线程更新GUI的信号类
class GuiUpdater(QtCore.QObject):
    update_signal = QtCore.pyqtSignal(object)

    def __init__(self):
        super().__init__()

    def update_gui(self, data):
        self.update_signal.emit(data)

# 主窗口类，继承自QMainWindow和Ui_MainWindow
class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 绑定按钮点击事件到相应的方法
        self.pushButton.clicked.connect(self.Button1_Method)
        self.pushButton_2.clicked.connect(self.Button2_Method)

        # 初始化变量
        self.difficulty = 80  # 难度
        self.waitTime = 10  # 等待时间
        self.started = False  # 标记是否已经开始
        self.isRunning = False  # 标记是否正在运行
        self.TargetPicCodeList = [i for i in range(1, 5)]  # 目标图片代码列表
        self.TargetPicPath = "images"  # 目标图片路径
        self.TargetPic = None  # 当前目标图片
        self.timeFlag=0   #标记是否需要刷新计时
        self.ComboNum = 0  # 连击数
        self.totalMark = 0  # 总得分
        self.t1 = Thread(target=self.RefreshFrame)  # 刷新帧的线程
        #self.t1.setDaemon(True)
        self.t2 = Thread(target=self.refreshBody)  # 刷新分数和目标图片的线程
        self.pause_event = Event()  # 暂停事件
        self.pause_event.set()  # 初始设置为暂停状态
        self.restart_event = Event()  # 重新开始事件
        self.pause_event_2 = Event()  # 暂停事件
        self.pause_event_2.set()  # 初始设置为暂停状态
        self.stop_thread=False

        self.gui_updater = GuiUpdater()  # GUI更新器
        self.gui_updater.update_signal.connect(self.update_gui)  # 连接信号与槽函数

        self.t1.start()  # 启动刷新帧的线程

    def closeEvent(self, event):
        self.stop_thread = True  
        self.isRunning = False  # 停止刷新帧的线程
        self.pause_event.clear()  # 设置暂停事件，以便退出刷新分数和目标图片的线程
        try:
            self.pause_event_2.clear()
            self.t1.join()
            VideoMain.finalize()
            
            self.t2.join()
        except Exception as e:
            print(str(e))
        print(self.t1.is_alive())
        
        event.accept()  # 关闭窗口

    def Button1_Method(self):
        try:
            if not self.started:
                self.startDance()
                self.started = True
                self.isRunning = True
                self.pushButton.setText("重新开始")
            else:
                self.restartDance()
                self.ComboNum = 0
                self.totalMark = 0
                self.gui_updater.update_gui({"text": f'得分:\n{round(self.totalMark,1)}', "label": 3})
                self.gui_updater.update_gui({"text": f'combo:\n{self.ComboNum}', "label": 4})
        except Exception as e:
            print(str(e))

    def Button2_Method(self):
        if self.isRunning:
            self.pauseDance()
            self.isRunning = False
        else:
            self.resumeDance()
            self.isRunning = True

    def getTargetFrame(self, TargetCode):
        fileName = self.TargetPicPath + "\\" + str(TargetCode) + ".png"
        pic = cv2.imread(fileName)
        return pic

    def startDance(self):
        self.t2.start()

    def RefreshFrame(self):
        while True:
            self.pause_event_2.wait()
            videoPic = VideoMain.getVideoFrame()
            image = qimage2ndarray.array2qimage(videoPic)
            self.gui_updater.update_gui({"image": image, "label": 1})
            time.sleep(0.1)
            if self.stop_thread:
                break

    def showTarget(self, TargetPicCode):
        targetPic = self.getTargetFrame(TargetPicCode)
        image = qimage2ndarray.array2qimage(targetPic)
        self.TargetPic = targetPic
        self.gui_updater.update_gui({"image": image, "label": 2})

    def getScore(self):
        try:
            mark = VideoMain.getScore(self.TargetPic)
            self.totalMark += mark
            if mark >= self.difficulty:
                self.ComboNum += 1
            else:
                self.ComboNum = 0
            self.gui_updater.update_gui({"text": f'得分:\n{round(self.totalMark,1)}', "label": 3})
            self.gui_updater.update_gui({"text": f'combo:\n{self.ComboNum}', "label": 4})
        except Exception as e:
            print(str(e))

    def Timer(self, T=int):
        now=time.time()
        t=now+T
        flag=1
        self.timeFlag=0
        while  now<t:
            realLeftTime=t-now
            time.sleep(0.001)
            leftTime=round(realLeftTime,2)
            if leftTime%1==0 and flag:
                self.gui_updater.update_gui({"text": f'剩余时间：\n{round(leftTime)}s', "label": 5})
                flag=0
            if (leftTime+0.5)%1==0:flag=1
            #print(leftTime)
            if self.restart_event.is_set() or self.stop_thread: return None
            self.pause_event.wait()
            now=time.time()
            if self.timeFlag:
                time.sleep(0.01)
                if self.timeFlag:
                    t=time.time()+realLeftTime
                    self.timeFlag=0
        return 1

    def restartDance(self):
        print('restart')
        self.restart_event.set()

    def refreshBody(self):
        while True:
            try:
                for TargetPicCode in self.TargetPicCodeList:
                    print(f'TargetPicCode:{TargetPicCode}')
                    self.showTarget(TargetPicCode)
                    self.pause_event.wait()
                    self.Timer(self.waitTime)
                    if self.restart_event.is_set()or self.stop_thread:
                        self.restart_event.clear()
                        break
                    self.pause_event.wait()
                    self.getScore()
                if self.stop_thread: break
            except Exception as e:
                print(str(e))

    def pauseDance(self):
        self.timeFlag=1
        self.pause_event.clear()
        self.pushButton_2.setText("继续")

    def resumeDance(self):
        self.pause_event.set()
        self.pushButton_2.setText("暂停")

    def update_gui(self, data):
        if "image" in data:
            if data["label"] == 1:
                self.label_1.setPixmap(QtGui.QPixmap.fromImage(data["image"]))
                self.label_1.setScaledContents(True)
            elif data["label"] == 2:
                self.label_2.setPixmap(QtGui.QPixmap.fromImage(data["image"]))
                self.label_2.setScaledContents(True)
        elif "text" in data:
            if data["label"] == 3:
                self.label_3.setText(data["text"])
            elif data["label"] == 4:
                self.label_4.setText(data["text"])
            elif data["label"] == 5:
                self.label_5.setText(data["text"])

# 主程序入口
if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        MyWindow = MyWindow()  # 创建主窗口对象
        MyWindow.show()  # 显示主窗口
        sys.exit(app.exec_())  # 运行应用事件循环
    except Exception as e:
        print(str(e))