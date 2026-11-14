import requests
url = "https://space.bilibili.com/3494363080428275" 
# 核心：添加PC浏览器的User-Agent，模拟Chrome浏览器
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://space.bilibili.com/"  # 可选：添加Referer
}
while 1:
    try:
        # 发送GET请求，禁止自动重定向（可选，避免被跳转到登录页）
        response = requests.get(url, headers=headers, allow_redirects=False)
        response.raise_for_status()  # 若状态码异常，抛出错误
        response.encoding = "utf-8" 
        网页内容=response.text
        p='账号，第一时间了解UP主动态。'
        截断=网页内容[网页内容.find(p)+len(p):]
        作者简介=截断[:截断.find('"/><')]
        print(作者简介)
    except requests.exceptions.RequestException as e:
        print(f"请求失败：{e}")
