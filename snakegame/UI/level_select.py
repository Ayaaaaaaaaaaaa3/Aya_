from tkinter import Tk, Frame, Button, Label
from config import UI_WIDTH, UI_HEIGHT

class LevelSelect:
    def __init__(self, master):
        self.master = master
        self.master.title("选择关卡")
        self.master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}")
        self.master.resizable(False, False)
        
        # 设置窗口居中
        master.update_idletasks()
        x = (master.winfo_screenwidth() // 2) - (UI_WIDTH // 2)
        y = (master.winfo_screenheight() // 2) - (UI_HEIGHT // 2)
        master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}+{x}+{y}")
        
        self.frame = Frame(self.master)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        self.label = Label(self.frame, text="请选择关卡", font=("Arial", 24))
        self.label.pack(pady=20)

        # 按钮样式
        button_style = {
            'font': ("Arial", 16),
            'width': 20
        }

        self.level_buttons = []
        for i in range(1, 6):  # 假设有5个关卡
            button = Button(self.frame, text=f"关卡 {i}", 
                           command=lambda level=i: self.select_level(level), 
                           **button_style)
            button.pack(pady=10)
            self.level_buttons.append(button)

        self.back_button = Button(self.frame, text="返回", 
                                 command=self.back_to_menu, **button_style)
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