from tkinter import Tk, Frame, Button, Label

class LevelSelect:
    def __init__(self, master):
        self.master = master
        self.master.title("选择关卡")
        self.frame = Frame(self.master)
        self.frame.pack()

        self.label = Label(self.frame, text="请选择关卡", font=("Arial", 24))
        self.label.pack(pady=20)

        self.level_buttons = []
        for i in range(1, 6):  # 假设有5个关卡
            button = Button(self.frame, text=f"关卡 {i}", command=lambda level=i: self.select_level(level))
            button.pack(pady=10)
            self.level_buttons.append(button)

        self.back_button = Button(self.frame, text="返回", command=self.back_to_menu)
        self.back_button.pack(pady=20)

    def select_level(self, level):
        print(f"选择了关卡 {level}")
        # 在这里可以添加进入游戏逻辑

    def back_to_menu(self):
        print("返回到开始菜单")
        # 在这里可以添加返回菜单的逻辑

if __name__ == "__main__":
    root = Tk()
    level_select = LevelSelect(root)
    root.mainloop()