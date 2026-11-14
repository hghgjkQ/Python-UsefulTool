import win32gui
import tkinter as tk
import pynput
import threading
import keyboard
import ctypes


class WindowFocusTracker:
    def __init__(self):
        self.running = 1
        self.pos = [[0.0, 0.0], [100.0, 100.0]]
        self.tar = {
            "窗口句柄": 0,
            "窗口左上角位置": (0, 0),
            "窗口右下角位置": (100, 100),
            "窗口宽度": 100,
            "窗口高度": 100,
        }
        self.root = None
        self.canvas = None
        self.mouse_listener = None
        self._line_id = None

    def _make_click_through(self):
        """设置窗口点击穿透（WS_EX_TRANSPARENT），等价于 Qt.WindowTransparentForInput"""
        try:
            hwnd = self.root.winfo_id()
            parent = ctypes.windll.user32.GetParent(hwnd)
            if parent:
                hwnd = parent
            GWL_EXSTYLE = -20
            WS_EX_LAYERED = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            styles = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT
            )
        except Exception:
            pass

    def get_focus_window_pos_size(self):
        """获取当前焦点窗口的位置和大小信息"""
        try:
            focus_hwnd = win32gui.GetForegroundWindow()
            if not focus_hwnd:
                return None
            left, top, right, bottom = win32gui.GetWindowRect(focus_hwnd)
            return {
                "窗口句柄": focus_hwnd,
                "窗口左上角位置": (left, top),
                "窗口右下角位置": (right, bottom),
                "窗口宽度": right - left,
                "窗口高度": bottom - top,
            }
        except Exception:
            return None

    def _animate(self):
        """平滑移动并重绘边框（替代原 paintEvent 中的插值逻辑）"""
        if not self.running:
            return
        try:
            tar = self.tar
            pos = self.pos
            pos[0][0] += (tar["窗口左上角位置"][0] + 5 - pos[0][0]) / 10
            pos[0][1] += (tar["窗口左上角位置"][1] - pos[0][1]) / 10
            pos[1][0] += (tar["窗口右下角位置"][0] - 5 - pos[1][0]) / 10
            pos[1][1] += (tar["窗口右下角位置"][1] - 5 - pos[1][1]) / 10

            x1, y1 = pos[0][0], pos[0][1]
            x2, y2 = pos[1][0], pos[1][1]
            coords = [x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]
            if self._line_id is None:
                self._line_id = self.canvas.create_line(
                    *coords, fill="#ff0000", width=10
                )
            else:
                self.canvas.coords(self._line_id, *coords)
        except Exception:
            pass
        self.root.after(10, self._animate)

    def on_mouse_move(self, x, y):
        """鼠标移动回调（非阻塞）"""
        if not self.running:
            return False
        info = self.get_focus_window_pos_size()
        if isinstance(info, dict):
            self.tar = info
        return True

    def start_mouse_listener(self):
        self.mouse_listener = pynput.mouse.Listener(on_move=self.on_mouse_move)
        self.mouse_listener.start()
        self.mouse_listener.join()

    def on_key_press(self, x):
        """空格键停止所有操作"""
        try:
            if x.event_type == "down" and x.name == "space":
                self.running = 0
                if self.mouse_listener and self.mouse_listener.is_alive():
                    self.mouse_listener.stop()
                keyboard.unhook_all()
                if self.root:
                    self.root.destroy()
        except Exception:
            pass

    def start_tracker(self):
        """
        阻塞式启动，返回最终的 tar（窗口跟踪信息字典）
        """
        self.root = tk.Tk()
        # 无边框 + 置顶
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        # 全屏
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{sw}x{sh}+0+0")
        # 透明背景（Windows 专用，magenta 作为透明色键）
        self.root.attributes("-transparentcolor", "magenta")
        self.root.config(bg="magenta")

        self.canvas = tk.Canvas(
            self.root, width=sw, height=sh,
            bg="magenta", highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # 确保窗口已映射后再设置点击穿透
        self.root.update_idletasks()
        self._make_click_through()

        keyboard.hook(self.on_key_press)
        threading.Thread(target=self.start_mouse_listener, daemon=True).start()

        self.root.after(10, self._animate)
        self.root.mainloop()
        return self.tar


if __name__ == "__main__":
    tracker = WindowFocusTracker()
    final_tar = tracker.start_tracker()
    print(f"程序完全退出，最终窗口信息：{final_tar}")
