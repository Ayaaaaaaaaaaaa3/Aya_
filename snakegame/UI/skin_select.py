from tkinter import Tk, Label, Button, Frame, StringVar, OptionMenu

class SkinSelect:
    def __init__(self, master):
        self.master = master
        self.master.title("选择皮肤")
        
        self.selected_skin = StringVar()
        self.skins = ["皮肤1", "皮肤2", "皮肤3", "皮肤4"]
        self.selected_skin.set(self.skins[0])  # 默认选择第一个皮肤

        self.create_widgets()

    def create_widgets(self):
        frame = Frame(self.master)
        frame.pack(pady=20)

        label = Label(frame, text="请选择贪吃蛇皮肤:")
        label.pack()

        skin_menu = OptionMenu(frame, self.selected_skin, *self.skins)
        skin_menu.pack()

        confirm_button = Button(frame, text="确认选择", command=self.confirm_selection)
        confirm_button.pack(pady=10)

        back_button = Button(frame, text="返回", command=self.master.quit)
        back_button.pack(pady=5)

    def confirm_selection(self):
        selected = self.selected_skin.get()
        print(f"已选择皮肤: {selected}")
        # 在这里可以添加代码来处理皮肤选择后的逻辑

if __name__ == "__main__":
    root = Tk()
    app = SkinSelect(root)
    root.mainloop()