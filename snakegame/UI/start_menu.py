from tkinter import Tk, Frame, Button, Label, Canvas
from config import UI_WIDTH, UI_HEIGHT
from PIL import Image, ImageTk  # 新增

class StartMenu:
    def __init__(self, master):
        self.master = master
        master.title("白蛇贪吃劫")
        master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}")
        master.resizable(False, False)
        
        # 加载背景图片（用假的文件名，可替换为实际图片）
        try:
            self.bg_image = Image.open("assets/start_bg.jpg")
            self.bg_image = self.bg_image.resize((UI_WIDTH, UI_HEIGHT))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except Exception:
            self.bg_photo = None
        
        # 用Canvas显示背景
        self.canvas = Canvas(master, width=UI_WIDTH, height=UI_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        if self.bg_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
        
        # 主色调（与背景图片主色调一致，可替换）
        main_color = '#225560'  # 深蓝绿色
        hover_color = '#6ec1e4'  # 浅蓝绿色
        
        # 在Canvas上放Frame和按钮，Frame放在右下角
        self.frame = Frame(master, bg='', highlightthickness=0)
        self.frame.place(relx=0.98, rely=0.98, anchor='se')  # 右下角对齐
        
        # 按钮样式
        button_style = {
            'font': ("Arial", 16),
            'width': 20,
            'bg': main_color,
            'activebackground': main_color,
            'bd': 2,  # 边框宽度
            'highlightthickness': 2,  # 高亮边框宽度
            'highlightbackground': 'black',  # 边框颜色
            'highlightcolor': 'black'
        }
        
        # 创建按钮并绑定悬停事件
        self.skin_button = Button(self.frame, text="选择皮肤", command=self.select_skin, **button_style)
        self.skin_button.pack(pady=0, anchor='e')
        self.skin_button.bind('<Enter>', lambda e: self.skin_button.config(bg=hover_color))
        self.skin_button.bind('<Leave>', lambda e: self.skin_button.config(bg=main_color))
        
        self.level_button = Button(self.frame, text="选择关卡", command=self.select_level, **button_style)
        self.level_button.pack(pady=0, anchor='e')
        self.level_button.bind('<Enter>', lambda e: self.level_button.config(bg=hover_color))
        self.level_button.bind('<Leave>', lambda e: self.level_button.config(bg=main_color))

        self.start_button = Button(self.frame, text="开始游戏", command=self.start_game, **button_style)
        self.start_button.pack(pady=0, anchor='e')
        self.start_button.bind('<Enter>', lambda e: self.start_button.config(bg=hover_color))
        self.start_button.bind('<Leave>', lambda e: self.start_button.config(bg=main_color))

        self.record_button = Button(self.frame, text="战绩记录", command=self.show_records, **button_style)
        self.record_button.pack(pady=0, anchor='e')
        self.record_button.bind('<Enter>', lambda e: self.record_button.config(bg=hover_color))
        self.record_button.bind('<Leave>', lambda e: self.record_button.config(bg=main_color))

    def select_skin(self):
        print("打开皮肤选择界面")

    def select_level(self):
        print("打开关卡选择界面")

    def start_game(self):
        print("开始游戏")

    def show_records(self):
        print("显示战绩记录")

if __name__ == "__main__":
    root = Tk()
    start_menu = StartMenu(root)
    root.mainloop()