from tkinter import Tk, Frame, Button, Label
from config import UI_WIDTH, UI_HEIGHT

LEVEL_COUNT = 10  # 与基础机制.py保持一致

class LevelSelect:
    def __init__(self, master, on_level_selected=None, on_back=None):
        self.master = master
        self.on_level_selected = on_level_selected
        self.on_back = on_back
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
        for i in range(1, LEVEL_COUNT + 1):  # 动态生成关卡按钮
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
        if self.on_level_selected:
            self.on_level_selected(level)

    def back_to_menu(self):
        print("返回到开始菜单")
        if self.on_back:
            self.on_back()

if __name__ == "__main__":
    root = Tk()
    level_select = LevelSelect(root)
    root.mainloop()