from PIL import ImageGrab, Image
import numpy as np
import ctypes
import ctypes.wintypes
import win32gui
import time
import win32ui
import win32con
from ctypes import windll

    
def 截图(x=0):
    screenshot = ImageGrab.grab(bbox=(362,399+x,504,413+x))  # 指定区域截图
    img_array = np.array(screenshot) # 2. 将图像转换为NumPy数组进行高效处理
    target_color = np.array([252, 252, 252]) # 3. 创建目标颜色数组 (252,252,252)
    mask = np.any(img_array[:, :, :3] != target_color, axis=-1) # 4. 创建掩码：标记所有非目标像素的位置
    rgba_array = np.dstack((img_array, np.full(img_array.shape[:2], 255, dtype=np.uint8))) # 5. 将非目标像素设置为透明（RGBA模式）
    rgba_array[mask, 3] = 0 # 6. 应用掩码：非目标像素设置完全透明 (alpha=0)
    result_img = Image.fromarray(rgba_array) # 7. 创建并保存结果图像
    return result_img.resize((71, 7), Image.NEAREST)

def 获取玩家角度(x=0):
    global 匹配集
    img=截图(x) #截屏
    width=img.width #获取结果长度
    img = np.array(img) #转为numpy图片
    alpha=img[:,:,3] #获取透明度组
    result=['+']*width #创建空目标
    for i in range(width): #遍历每一列
        if np.any(alpha[:,i]>0): #如果不是空列
            result[i]=''.join([str(x) for x in(alpha[:,i]>0).astype(int)]) #总结列名
        else: #如果是空列
            if i!=0: #处理
                if result[i-1] in (None,'+'):
                    result[i]=None
    out=[hex(int(i,2))[2:] for i in [x for x in (''.join([i for i in result if i!=None])).split('+') if x!='']] #得出结论
    out=''.join([匹配集[i] for i in out]) #转换为可读文本
    return out
        
def 获取玩家坐标(窗口=None,x=0):
    global 匹配集
    screenshot = ImageGrab.grab(bbox=(0,359+x,1920,373+x))  # 指定区域截图
    img_array = np.array(screenshot) # 2. 将图像转换为NumPy数组进行高效处理
    target_color = np.array([252, 252, 252]) # 3. 创建目标颜色数组 (252,252,252)
    mask = np.any(img_array[:, :, :3] != target_color, axis=-1) # 4. 创建掩码：标记所有非目标像素的位置
    rgba_array = np.dstack((img_array, np.full(img_array.shape[:2], 255, dtype=np.uint8))) # 5. 将非目标像素设置为透明（RGBA模式）
    rgba_array[mask, 3] = 0 # 6. 应用掩码：非目标像素设置完全透明 (alpha=0)
    result_img = Image.fromarray(rgba_array) # 7. 创建并保存结果图像
    img = result_img.resize((960, 7), Image.NEAREST)
    width=img.width #获取结果长度
    img = np.array(img) #转为numpy图片
    alpha=img[:,:,3] #获取透明度组
    result=['+']*width #创建空目标
    for i in range(width): #遍历每一列
        if np.any(alpha[:,i]>0): #如果不是空列
            result[i]=''.join([str(x) for x in(alpha[:,i]>0).astype(int)]) #总结列名
        else: #如果是空列
            if i!=0: #处理
                if result[i-1] in (None,'+'):
                    result[i]=None
    out=[hex(int(i,2))[2:] for i in [x for x in (''.join([i for i in result if i!=None])).split('+') if x!='']] #得出结论
    out=''.join([匹配集[i] for i in out]) #转换为可读文本
    return out.split('.')

# 定义必要的Windows API函数和结构
user32 = ctypes.WinDLL('user32')

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _fields_ = [("type", ctypes.c_ulong), ("mi", _INPUT)]

# 常量定义
INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001

def move_mouse_relative(dx, dy):
    ctypes.windll.user32.mouse_event(0x0001, dx, dy, 0, 0)

def rotate_view(dx, dy, sensitivity=(100/15)):
    """转动游戏视角的核心函数"""
    # 应用灵敏度
    dx = int(dx * sensitivity)
    dy = int(dy * sensitivity)
    
    # 移动鼠标（相对移动）
    move_mouse_relative(dx, dy)


匹配集={
    '81020408': '-',
    '1': '.',
    '10c21840': '/',
    '3e8b268be': '0',
    '143fc081': '1',
    '238b264b3': '2',
    '2283264b6': '3',
    'c289227f': '4',
    '72a3468ce': '5',
    '1e5326486': '6',
    '60811e470': '7',
    '3693264b6': '8',
    '30932653c': '9'
    }


