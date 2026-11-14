from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer
import sys

class ScreenDrawWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 1. 核心窗口配置：透明、顶层、无焦点、无边框
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |  # 始终顶层
            Qt.FramelessWindowHint |   # 无边框
            Qt.Tool |                  # 无任务栏图标，无焦点
            Qt.WindowTransparentForInput  # 关键：窗口不接收输入事件，底层可操作
        )
        # 设置窗口全屏且透明
        self.setGeometry(QApplication.desktop().screenGeometry())
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 透明背景
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)  # 显示时不激活窗口（不抢占焦点）

    def paintEvent(self, event):
        # 4. 自定义绘制：绘制矩形和圆形
        painter = QPainter(self)
        # 绘制蓝色矩形
        painter.setBrush(QColor(0, 0, 255, 128))  # 最后一个参数是透明度（0-255）
        painter.drawRect(100, 100, 150, 100)
        # 绘制黄色圆形
        painter.setBrush(QColor(255, 255, 0, 128))
        painter.drawEllipse(300, 100, 100, 100)
        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 关键：设置应用程序不抢占焦点
    app.setQuitOnLastWindowClosed(True)
    window = ScreenDrawWidget()
    window.show()
    sys.exit(app.exec_())
