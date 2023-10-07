import sys
import os
import configparser
import platform
import queue
import math
import base64
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QTimeEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QSystemTrayIcon,
    QProgressBar,
    QMainWindow,
    QDialog,
)
from PySide6.QtCore import Qt, QTime, QTimer, Signal, QObject, QSize, QByteArray
from PySide6.QtGui import QIcon, QAction, QColor, QPainter, QPalette, QFont, QBrush, QPen, QPixmap, QMovie

from pic import base64_image


info = """
本软件完全免费，请勿相信任何付费内容！
本软件代码完全开源，任何人二次修改创作均与本人无关，请勿用作不法用途
"""


def base64ToByte(imgstr:str):
    decoded_data = base64.b64decode(imgstr)
    byte_array = QByteArray(decoded_data)
    return byte_array

class CircleLabel(QLabel):
    def __init__(self, num, parent=None):
        super().__init__(parent)
        self.angle = 270  # 初始角度
        self.animation_speed = 1  # 动画速度
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateAnimation)
        self.timer.timeout.connect(self.userUpdateAnimation)
        self.timer.start(15)
        self.num = num
        self.flag = 0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        center = self.rect().center()
        radius = min(self.width(), self.height()) / 8

        # 设置画笔样式
        pen = QPen()
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(0.5)
        painter.setPen(pen)

        # 计算圆点的位置
        dot_radius = 3
        dot_angle = math.radians(self.angle)  # 将角度转换为弧度
        dot_x = center.x() + radius * math.cos(dot_angle)
        dot_y = center.y() + radius * math.sin(dot_angle)

        # 设置画刷样式并绘制圆点
        brush = QBrush(QColor(255, 255, 255))
        painter.setBrush(brush)
        painter.drawEllipse(
            dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2
        )

    def updateAnimation(self):
        if 90 <= self.angle < 270:  # 在π*3/2之后，减小动画速度使其变慢
            self.animation_speed -= 0.1
        elif (self.angle >= 270 and self.angle < 360) or (
            self.angle >= 0 and self.angle < 90
        ):  # 在π/2之前，增加动画速度使其变快
            self.animation_speed += 0.1

        self.angle += self.animation_speed

        if self.angle >= 360:
            self.angle = 0

        self.update()

    def userUpdateAnimation(self):
        self.flag += 1

        if self.num <= self.flag:
            return

        self.updateAnimation()


# 创建一个继承自QMainWindow的类，用于实现关机动画窗口
class ShutdownAnimationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("关机动画")
        self.screen_width = QApplication.primaryScreen().size().width()
        self.screen_height = QApplication.primaryScreen().size().height()
        self.setGeometry(0, 0, self.screen_width, self.screen_height)

        # 创建一个中心部件，并将其设置为窗口的中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 初始化动画步骤和定时器
        self.animation_step = 0
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(2)  # 设置动画帧率为60毫秒一帧

        num = [1, 7, 13, 19, 25, 31]

        labels = []
        for i in range(6):
            label = CircleLabel(num[i], self)
            label.setGeometry(
                (self.screen_width - 300) / 2,
                (self.screen_height - 300) / 2 - 30,
                300,
                300,
            )
            labels.append(label)

        # 创建一个标签并将其添加到布局中
        self.label = QLabel("正在关机", self)
        self.label.setFont(QFont("微软雅黑", 16))
        self.label.setStyleSheet("color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(
            (self.screen_width - 300) / 2, (self.screen_height - 300) / 2 + 30, 300, 300
        )

    def update_animation(self):
        # 更新动画步骤，触发重绘事件
        if self.animation_step < 100:
            self.animation_step += 1
            self.update()
        else:
            self.animation_timer.stop()  # 动画完成后停止定时器

    def paintEvent(self, event):
        # 在重绘事件中绘制动画效果
        palette = self.centralWidget().palette()
        gradient = QPalette()

        # 根据动画步骤设置窗口背景颜色的透明度
        gradient.setColor(
            QPalette.Window, QColor(0, 103, 191, self.animation_step * 255 // 100)
        )

        # 设置中心部件的背景
        palette.setBrush(QPalette.Window, gradient.window())
        self.centralWidget().setAutoFillBackground(True)
        self.centralWidget().setPalette(palette)


class Configs:
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read("config.ini", encoding="utf-8")

    def initIni(self):
        self.config["SETTINGS"] = {
            "AUTOHIDE": "true",
            "WORKTIME": "08:00",
            "OFFTIME": "17:30",
            "JOKE": "true",
        }
        self.writeConfig()

    def getAutoHide(self):
        self.auto_hide = self.config["SETTINGS"]["AUTOHIDE"]

    def getStart(self):
        self.work_time = self.config["SETTINGS"]["WORKTIME"]

    def getEnd(self):
        self.off_time = self.config["SETTINGS"]["OFFTIME"]

    def getJoke(self):
        self.joke = self.config["SETTINGS"]["JOKE"]

    def getMessages(self):
        msg_queue = queue.Queue()
        for tip in self.config["MESSAGES"]:
            msg_queue.put(self.config["MESSAGES"][tip])
        self.msg_queue = msg_queue

    def getMsg(self):
        while not self.msg_queue.empty():
            msg = self.msg_queue.get()
            return msg

    def setAutoHide(self):
        self.config["SETTINGS"]["AUTOHIDE"] = "true"
        self.writeConfig()

    def setStart(self, start):
        self.config["SETTINGS"]["WORKTIME"] = start
        self.writeConfig()

    def setEnd(self, end):
        self.config["SETTINGS"]["OFFTIME"] = end
        self.writeConfig()

    def setJoke(self, joke):
        self.config["SETTINGS"]["JOKE"] = joke
        self.writeConfig()

    def writeConfig(self):
        with open("config.ini", "w", encoding="utf-8") as configfile:
            self.config.write(configfile)


class Gif():
    def __init__(self) :
        self.getGifsPath()

    def getGifsPath(self):
        directory_path = "gif"

        path_queue = queue.Queue()

        for root, dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                path_queue.put(file_path)
        self.gifs_path_queue = path_queue

    def getGifsNum(self):
        return self.gifs_path_queue.qsize()

    def getGif(self):
        while not self.gifs_path_queue.empty():
            file_path = self.gifs_path_queue.get()
            return file_path

    def isGif(self, filename):
        with open(filename, 'rb') as file:
            header = file.read(6)  # 读取文件的前6个字节
            return header == b'GIF89a' or header == b'GIF87a'


class MyDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.gifs = Gif()
        self.conf = Configs()
        self.conf.getMessages()
        self.conf.getJoke()
        self.emitter = MyEmitter()

    def createDialog(self):
        self.setWindowTitle("下班提示")

        # 创建对话框上的控件
        self.label = QLabel(self.conf.getMsg())

        # 创建一个显示图片的QLabel
        self.image_label = QLabel(self)
        self.updateImage(self.gifs.getGif())

        self.ok_button = QPushButton("马上关机")
        self.no_button = QPushButton("取消")
        self.ok_button.clicked.connect(self.accept)
        self.no_button.clicked.connect(self.reject)

        # 设置对话框布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.label)

        # 创建水平布局并添加按钮
        row_layout = QHBoxLayout()
        row_layout.addWidget(self.ok_button)
        row_layout.addWidget(self.no_button)

        layout.addLayout(row_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showDialog)

    def reject(self):
        self.hide()
        if self.conf.joke == 'true':
            self.timer.start(1000)
            if self.gifs.getGifsNum() == 0:
                self.emitter.exit_app_signal.emit()
        else:
            self.emitter.exit_app_signal.emit()

    def accept(self):
        super().accept()
        self.emitter.shutdown_signal.emit()

    def updateImage(self, image_path):
        if self.gifs.isGif(image_path):
            movie = QMovie(image_path)
            movie.setScaledSize(QSize(200, 200))
            movie.setCacheMode(QMovie.CacheAll)
            movie.setSpeed(100)
            self.image_label.setMovie(movie)
            movie.start()
        else:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(200, 200)
            self.image_label.setPixmap(pixmap)


    def changeImage(self, new_image_path:str):
        self.updateImage(new_image_path)

    def changeButtonText(self, text):
        self.no_button.setText(text)

    def changeLabelText(self, text):
        self.label.setText(text)

    def closeEvent(self, event):
        self.hide()
        self.timer.start(1000)
        event.ignore()

    def showDialog(self):
        # 停止计时器并显示对话框
        self.timer.stop()
        gif_num = self.gifs.getGifsNum()
        if gif_num == 3:
            self.emitter.shutdown_window_show_signal.emit()
            self.changeLabelText(self.conf.getMsg())
            self.changeImage(self.gifs.getGif())
            return
        if gif_num > 1:
            self.changeLabelText(self.conf.getMsg())
            self.changeImage(self.gifs.getGif())
            self.changeButtonText("稍后提示")
            self.show()
            return
        elif gif_num > 0:
            self.changeLabelText(self.conf.getMsg())
            self.changeImage(self.gifs.getGif())
            self.ok_button.setEnabled(False)
            self.changeButtonText("拜拜卷王")
            self.show()


class TipDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("提示")

        self.label = QLabel(info)

        self.image_label = QLabel(self)

        png = base64ToByte(base64_image)
        pixmap = QPixmap()
        pixmap.loadFromData(png)
        pixmap = pixmap.scaled(600, 200)
        self.image_label.setPixmap(pixmap)

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        layout.addWidget(self.label)


class MyEmitter(QObject):
    # 定义一个自定义信号，可以带参数
    work_time_signal = Signal(str)
    off_time_signal = Signal(str)
    hide_signal = Signal()
    exit_app_signal = Signal()
    shutdown_window_show_signal = Signal()
    shutdown_signal = Signal()
    work_done_signal = Signal()


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.emitter = MyEmitter()
        self.work_time = ""
        self.off_time = ""

    def initUI(self):
        self.setWindowTitle("设置")
        self.createWindow()
        self.createTrayIcon()
        self.process_bar_window = WorkWindow()
        self.process_bar_window.initUI()
        self.process_bar_window.setTimes(conf.work_time, conf.off_time)
        self.process_bar_window.emitter.work_done_signal.connect(self.hideProcessBar)
        self.process_bar_window.emitter.work_done_signal.connect(self.showDialog)
        self.shutdown_window = ShutdownAnimationWindow()
        self.shutdown_dialog = MyDialog()
        self.shutdown_dialog.createDialog()
        self.shutdown_dialog.emitter.shutdown_signal.connect(self.shutdown)
        self.shutdown_dialog.emitter.shutdown_window_show_signal.connect(self.shutdownWindow)
        self.shutdown_dialog.emitter.exit_app_signal.connect(self.onExitClicked)
        self.tip_dialog = TipDialog()

    def createWindow(self):
        self.setWindowTitle("设置")
        self.setWindowIcon(QIcon("./icon.ico"))
        self.setFixedSize(200, 120)

        # 创建窗口布局
        layout = QVBoxLayout()

        # 第一行：上班时间输入框
        row1_layout = QHBoxLayout()
        self.label_work_time = QLabel("上班时间：")
        self.input_work_time = QTimeEdit(self)
        row1_layout.addWidget(self.label_work_time)
        row1_layout.addWidget(self.input_work_time)
        layout.addLayout(row1_layout)

        # 第二行：下班时间输入框
        row2_layout = QHBoxLayout()
        self.label_off_time = QLabel("下班时间：")
        self.input_off_time = QTimeEdit(self)
        row2_layout.addWidget(self.label_off_time)
        row2_layout.addWidget(self.input_off_time)
        layout.addLayout(row2_layout)

        # 第三行：确定和退出按钮
        row3_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("确定", self)
        self.btn_confirm.clicked.connect(self.onConfirmClicked)  # 连接确定按钮点击事件
        self.btn_exit = QPushButton("退出", self)
        self.btn_exit.clicked.connect(self.onExitClicked)  # 连接退出按钮点击事件
        row3_layout.addWidget(self.btn_confirm)
        row3_layout.addWidget(self.btn_exit)
        layout.addLayout(row3_layout)

        row4_layout = QHBoxLayout()
        self.Label_info = QPushButton("关于本程序", self)
        self.Label_info.clicked.connect(self.showTipDilaog)
        self.Label_info.setFlat(True)
        self.Label_info.setStyleSheet("color: blue;")
        row4_layout.addWidget(self.Label_info)
        layout.addLayout(row4_layout)

        # 设置整体布局
        self.setLayout(layout)

    def onConfirmClicked(self):
        work_time, off_time = self.getTimeEdit()
        self.emitter.work_time_signal.emit(work_time)
        self.emitter.off_time_signal.emit(off_time)
        self.emitter.hide_signal.emit()
        self.hide()
        self.process_bar_window.setTimes(conf.work_time, conf.off_time)
        self.process_bar_window.show()

    def onExitClicked(self):
        QApplication.quit()

    def openConfFile(self):
        os.system(f"notepad config.ini")

    def createTrayIcon(self):
        self.tray_menu = QMenu(self)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("icon.png"))
        # self.tray_icon.setToolTip("无边框浮窗示例")
        self.tray_icon.setContextMenu(self.tray_menu)

        set_action = QAction("高级设置", self)
        set_action.triggered.connect(self.openConfFile)

        show_action = QAction("打开设置", self)
        show_action.triggered.connect(self.show)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.onExitClicked)

        self.tray_menu.addAction(show_action)
        self.tray_menu.addAction(set_action)
        self.tray_menu.addAction(exit_action)
        self.tray_icon.show()

    def setTimeEdit(self, work_time: str, off_time: str):
        self.work_time = QTime.fromString(work_time, "hh:mm")
        self.off_time = QTime.fromString(off_time, "hh:mm")
        self.input_work_time.setTime(self.work_time)
        self.input_off_time.setTime(self.off_time)

    def getTimeEdit(self):
        return self.input_work_time.time().toString(
            "hh:mm"
        ), self.input_off_time.time().toString("hh:mm")

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def shutdown(self):
        system_platform = platform.system()

        if system_platform == "Windows":
            # 在Windows上执行关机命令
            os.system("shutdown /s /t 0")
        elif system_platform == "Darwin" or system_platform == "Linux":
            # 在macOS和Linux上执行关机命令，需要管理员权限
            os.system("sudo shutdown -h now")
        else:
            print("不支持的操作系统")

    def showDialog(self):
        self.shutdown_dialog.show()

    def hideShutDownWindow(self):
        self.shutdown_window.hide()

    def hideProcessBar(self):
        self.process_bar_window.hide()

    def shutdownWindow(self):
        self.shutdown_window.showFullScreen()
        timer = QTimer(self)
        timer.setSingleShot(True)
        timer.timeout.connect(self.hideShutDownWindow)
        timer.timeout.connect(self.showDialog)
        timer.start(3000)

    def showTipDilaog(self):
        self.tip_dialog.show()


class WorkWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.screen_w = QApplication.primaryScreen().size().width()
        self.window_w = 0
        self.window_h = 0
        self.timer = None
        self.percentage = 0
        self.emitter = MyEmitter()

    def initUI(self):
        self.createWindow()
        self.createProcessBar()
        self.createTimer()

    def setTimes(self, work_time, off_time):
        self.work_time = work_time
        self.off_time = off_time

    def createTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgressBar)
        self.timer.start(1000)  # 每秒更新一次进度条

    def createWindow(self, height=1):
        self.setGeometry(0, 0, self.screen_w, height)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)  # 将窗口设置为无边框，不显示任务栏图标
        self.setWindowFlag(Qt.WindowStaysOnTopHint)  # 将窗口置顶
        self.window_w = self.width()
        self.window_h = self.height()

    def createProcessBar(self):
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(0, 0, self.window_w, self.window_h)
        self.progress_bar.setValue(self.percentage * 100)
        self.progress_bar.setTextVisible(False)

    def getTimePercentage(self):
        current_time = QTime.currentTime()

        work_time = QTime.fromString(self.work_time, "hh:mm")
        off_time = QTime.fromString(self.off_time, "hh:mm")

        time_difference = current_time.secsTo(work_time)
        all_difference = off_time.secsTo(work_time)

        percentage = time_difference / all_difference
        self.percentage = float("{:.4}".format(percentage))

    def updateProgressBar(self):
        current_value = self.progress_bar.value()
        if current_value < 100:
            self.getTimePercentage()
            percentage = min(self.percentage * 100, 100)
            self.progress_bar.setValue(percentage)
        else:
            self.emitter.work_done_signal.emit()
            # 销毁信号/ 终止timer
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    conf = Configs()
    conf.getAutoHide()
    conf.getStart()
    conf.getEnd()
    conf.getJoke()
    conf.getMessages()

    window = SettingsWindow()
    window.initUI()
    window.emitter.work_time_signal.connect(conf.setStart)
    window.emitter.off_time_signal.connect(conf.setEnd)
    window.emitter.hide_signal.connect(conf.getStart)
    window.emitter.hide_signal.connect(conf.getEnd)
    window.emitter.hide_signal.connect(conf.setAutoHide)
    window.emitter.hide_signal.connect(window.process_bar_window.updateProgressBar)
    window.setTimeEdit(conf.work_time, conf.off_time)

    if conf.auto_hide == "true":
        window.process_bar_window.show()
    else:
        window.show()

    sys.exit(app.exec())
