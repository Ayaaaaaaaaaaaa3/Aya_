from tkinter import Tk, Frame, Button, Label

class StartMenu:
    def __init__(self, master):
        self.master = master
        master.title("白蛇传 贪吃蛇游戏")
        
        self.label = Label(master, text="欢迎来到白蛇传贪吃蛇游戏", font=("Arial", 24))
        self.label.pack(pady=20)

        self.skin_button = Button(master, text="选择皮肤", command=self.select_skin, font=("Arial", 16))
        self.skin_button.pack(pady=10)

        self.level_button = Button(master, text="选择关卡", command=self.select_level, font=("Arial", 16))
        self.level_button.pack(pady=10)

        self.start_button = Button(master, text="开始游戏", command=self.start_game, font=("Arial", 16))
        self.start_button.pack(pady=10)

        self.record_button = Button(master, text="战绩记录", command=self.show_records, font=("Arial", 16))
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