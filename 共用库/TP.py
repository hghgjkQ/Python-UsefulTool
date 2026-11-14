import time
import ctypes
import numpy as np
import pytesseract
import win32gui
import win32ui
import win32con
from PIL import Image, ImageEnhance

def capture_window(hw):
    """截图函数"""
    hd = md = sd = sb = None
    try:
        l, t, r, b = (0, 0, 1920, 1080)
        if not win32gui.IsWindowVisible(hw) or win32gui.IsIconic(hw):
            return None

        hd = win32gui.GetWindowDC(hw)
        md = win32ui.CreateDCFromHandle(hd)
        sd = md.CreateCompatibleDC()
        sb = win32ui.CreateBitmap()
        sb.CreateCompatibleBitmap(md, r - l, b - t)
        sd.SelectObject(sb)
        # 使用BitBlt从指定起点复制图像
        sd.BitBlt((0, 0), (r - l, b - t), md, (l, t), win32con.SRCCOPY)
        # 转换为PIL图像
        bmpinfo = sb.GetInfo()
        bmpstr = sb.GetBitmapBits(True)
        im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        return im
    except Exception as e:
        print(f"截图失败: {e}")
        return None
    finally:
        for o in [sb, sd, md, hd]:
            if o:
                try:
                    if isinstance(o, win32ui.CBitmap):
                        win32gui.DeleteObject(o.GetHandle())
                    elif isinstance(o, win32ui.CDC):
                        o.DeleteDC()
                    else:
                        win32gui.ReleaseDC(hw, o)
                except:
                    pass

def process_image_for_ocr(image):
    """处理图像以优化OCR识别"""
    # 保存原始截图用于调试
    image.save('a.png')
    
    # 转换为RGBA数组进行处理
    arr = np.array(image.convert('RGBA'))
    
    # 创建颜色掩码，过滤特定颜色
    mask = np.zeros(arr.shape[:2], bool)
    colors_to_filter = ('#EDEDED', '#95EC69')
    
    for color in colors_to_filter:
        # 将十六进制颜色转换为RGB元组
        rgb_color = tuple(int(color[1:][i:i+2], 16) for i in (0, 2, 4))
        # 计算颜色差异并创建掩码
        color_diff = np.abs(arr[..., :3] - rgb_color).sum(2)
        mask |= color_diff <= 10
    
    # 将匹配的颜色设置为透明
    arr[mask] = [255, 255, 255, 0]
    
    # 提取alpha通道
    alpha = np.array(Image.fromarray(arr).split()[-1])
    
    # 找到非透明区域的边界
    coords = np.column_stack(np.where(alpha > 0))
    
    # 裁剪图像到有效区域
    if coords.size:
        min_y, min_x = coords.min(0)
        max_y, max_x = coords.max(0)
        crop = Image.fromarray(arr).crop((min_x, min_y, max_x, max_y))
    else:
        crop = Image.fromarray(arr)
    
    # 增强对比度
    gray_image = crop.convert('L')
    enh = ImageEnhance.Contrast(gray_image)
    enhanced_image = enh.enhance(2.0)
    
    return enhanced_image


    
