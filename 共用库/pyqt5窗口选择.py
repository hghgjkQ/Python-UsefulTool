import win32gui
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QPointF, QCoreApplication, QTimer
import pynput
import time
import sys
import threading
import keyboard

class WindowFocusTracker:
    def __init__(self):
        # 初始化类属性，替代全局变量，线程安全初始化
        self.running = 1  # 改用英文命名，避免编码问题
        self.pos = [[0.0, 0.0], [100.0, 100.0]]
        self.tar = {
            "窗口句柄": 0,
            "窗口左上角位置": (0, 0),
            "窗口右下角位置": (100, 100),
            "窗口宽度": 100,
            "窗口高度": 100
        }
        self.app = None
        self.window = None
        self.mouse_listener = None  # 保存鼠标监听器实例，方便主动停止

    class ScreenDrawWidget(QWidget):
        """内嵌绘图窗口类，用于绘制窗口边框"""
        def __init__(self, parent_tracker):
            super().__init__()
            self.parent_tracker = parent_tracker
            self.init_ui()

        def init_ui(self):
            # 窗口核心配置
            self.setWindowFlags(
                Qt.WindowStaysOnTopHint |
                Qt.FramelessWindowHint |
                Qt.Tool |
                Qt.WindowTransparentForInput
            )
            self.setGeometry(QApplication.desktop().screenGeometry())
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        def paintEvent(self, event):
            try:
                tar = self.parent_tracker.tar
                pos = self.parent_tracker.pos

                # 平滑移动计算（避免属性篡改异常）
                pos[0][0] += (tar['窗口左上角位置'][0] + 5 - pos[0][0]) / 10
                pos[0][1] += (tar['窗口左上角位置'][1] - pos[0][1]) / 10
                pos[1][0] += (tar['窗口右下角位置'][0] - 5 - pos[1][0]) / 10
                pos[1][1] += (tar['窗口右下角位置'][1] - 5 - pos[1][1]) / 10

                painter = QPainter(self)
                painter.setPen(QPen(QColor(255, 0, 0, 128), 10, Qt.SolidLine))
                painter.setBrush(QColor(255, 0, 0, 0))

                # 绘制矩形边框
                left_top = (pos[0][0], pos[0][1])
                right_bottom = (pos[1][0], pos[1][1])
                painter.drawPolyline(
                    QPointF(left_top[0], left_top[1]),
                    QPointF(right_bottom[0], left_top[1]),
                    QPointF(right_bottom[0], right_bottom[1]),
                    QPointF(left_top[0], right_bottom[1]),
                    QPointF(left_top[0], left_top[1])
                )
                painter.end()
            except Exception as e:
                # 异常不阻塞程序
                pass

    def get_focus_window_pos_size(self):
        """获取当前焦点窗口的位置和大小信息"""
        try:
            focus_hwnd = win32gui.GetForegroundWindow()
            if not focus_hwnd:
                return None
            window_rect = win32gui.GetWindowRect(focus_hwnd)
            left, top, right, bottom = window_rect
            width = right - left
            height = bottom - top
            return {
                "窗口句柄": focus_hwnd,
                "窗口左上角位置": (left, top),
                "窗口右下角位置": (right, bottom),
                "窗口宽度": width,
                "窗口高度": height
            }
        except Exception as e:
            return None

    def window_update_loop(self):
        """窗口更新循环（替代原有次进程，增加容错）"""
        while self.running:
            if self.window and self.window.isVisible():
                try:
                    self.window.update()
                except Exception as e:
                    pass
            time.sleep(0.01)  # 降低循环频率，减少资源占用


    def on_mouse_move(self, x, y):
        """鼠标移动回调函数（非阻塞，替代原有for循环阻塞）"""
        if not self.running:
            return False  # 返回False停止监听器
        focus_window_info = self.get_focus_window_pos_size()
        if isinstance(focus_window_info, dict):
            self.tar = focus_window_info
        return True

    def start_mouse_listener(self):
        """启动鼠标监听（非阻塞模式，解决卡死核心）"""
        self.mouse_listener = pynput.mouse.Listener(on_move=self.on_mouse_move)
        self.mouse_listener.start()
        # 监听线程退出等待
        self.mouse_listener.join()


    def on_key_press(self, x):
        """键盘回调，空格键停止所有操作"""
        try:
            if x.event_type == 'down' and x.name == 'space':

                # 1. 设置停止标志
                self.running = 0
                # 2. 停止鼠标监听器（关键：解决pynput阻塞卡死）
                if self.mouse_listener and self.mouse_listener.is_alive():
                    self.mouse_listener.stop()
                # 3. 解除所有键盘钩子
                keyboard.unhook_all()
                # 4. 关闭窗口
                if self.window:
                    self.window.close()
                # 5. 终止Qt事件循环（核心：退出阻塞）
                if self.app:
                    QCoreApplication.quit()

        except Exception as e:
            pass

    def start_tracker(self):
        """
        阻塞式启动函数，解决卡死问题
        返回值：最终的tar（窗口跟踪信息字典）
        """
        # 初始化Qt应用
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(True)

        # 创建绘图窗口
        self.window = self.ScreenDrawWidget(self)

        # 注册键盘钩子
        keyboard.hook(self.on_key_press)

        # 启动子线程（守护线程，避免资源泄露）
        # 窗口更新线程
        threading.Thread(target=self.window_update_loop, daemon=True).start()
        # 鼠标监听线程（非阻塞模式）
        threading.Thread(target=self.start_mouse_listener, daemon=True).start()

        # 显示窗口
        self.window.show()

        # 进入Qt事件循环（阻塞，直到主动调用quit()）
        self.app.exec_()

        # 返回最终tar信息
        return self.tar

if __name__ == '__main__':
    # 创建跟踪器实例
    tracker = WindowFocusTracker()
    # 启动跟踪（无卡死，正常退出）
    final_tar = tracker.start_tracker()
    # 打印最终结果
    print(f"程序完全退出，最终窗口信息：{final_tar}")
