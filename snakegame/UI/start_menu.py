from tkinter import Tk, Frame, Button, Label
from config import UI_WIDTH, UI_HEIGHT

class StartMenu:
    def __init__(self, master):
        self.master = master
        master.title("白蛇传 贪吃蛇游戏")
        master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}")
        master.resizable(False, False)
        
        # 设置窗口居中
        master.update_idletasks()
        x = (master.winfo_screenwidth() // 2) - (UI_WIDTH // 2)
        y = (master.winfo_screenheight() // 2) - (UI_HEIGHT // 2)
        master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}+{x}+{y}")
        
        self.frame = Frame(master)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # 标题
        self.label = Label(self.frame, text="欢迎来到白蛇传贪吃蛇游戏", font=("Arial", 24))
        self.label.pack(pady=20)

        # 按钮样式
        button_style = {
            'font': ("Arial", 16),
            'width': 20
        }
        
        self.skin_button = Button(self.frame, text="选择皮肤", 
                                 command=self.select_skin, **button_style)
        self.skin_button.pack(pady=10)
        
        self.level_button = Button(self.frame, text="选择关卡", 
                                  command=self.select_level, **button_style)
        self.level_button.pack(pady=10)

        self.start_button = Button(self.frame, text="开始游戏", 
                                  command=self.start_game, **button_style)
        self.start_button.pack(pady=10)

        self.record_button = Button(self.frame, text="战绩记录", 
                                   command=self.show_records, **button_style)
        self.record_button.pack(pady=10)

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