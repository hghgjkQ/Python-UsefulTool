def p(文本, x, c="#000000", **a):  # 默认颜色为黑色
    # 创建一个唯一的标签名
    tag_name = f"color_{len(文本.tag_names())}"
    # 配置颜色标签
    文本.tag_configure(tag_name, foreground=c,** a)
    # 插入文本并应用颜色标签
    文本.insert('end', x + "\n", tag_name)
    文本.see(tk.END)
