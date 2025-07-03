from tkinter import Tk, Frame, Button, Label, Canvas
from config import UI_WIDTH, UI_HEIGHT
from PIL import Image, ImageTk

class EndMenu:
    def __init__(self, master, on_restart=None, on_quit=None):
        self.master = master
        self.on_restart = on_restart
        self.on_quit = on_quit
        master.title("游戏结束")
        master.geometry(f"{UI_WIDTH}x{UI_HEIGHT}")
        master.resizable(False, False)

        # 加载背景图片（可替换为实际图片）
        try:
            self.bg_image = Image.open("assets/end_bg.jpg")
            self.bg_image = self.bg_image.resize((UI_WIDTH, UI_HEIGHT))
            self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        except Exception:
            self.bg_photo = None

        # 用Canvas显示背景
        self.canvas = Canvas(master, width=UI_WIDTH, height=UI_HEIGHT, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        if self.bg_photo:
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)
            self.master._keep_bg_photo = self.bg_photo  # 彻底防止被回收
        self._keep_bg_photo = self.bg_photo  # 保险

        # Frame放在Canvas上
        self.frame = Frame(self.canvas, bg='', highlightthickness=0)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')

        # 按钮样式
        main_color = '#225560'
        hover_color = '#6ec1e4'
        button_style = {
            'font': ("Arial", 18),
            'width': 16,
            'bg': main_color,
            'activebackground': main_color,
            'fg': 'white',
            'bd': 2,
            'highlightthickness': 2,
            'highlightbackground': 'black',
            'highlightcolor': 'black'
        }

        self.restart_button = Button(self.frame, text="重新开始", command=self.restart, **button_style)
        self.restart_button.pack(pady=20)
        self.restart_button.bind('<Enter>', lambda e: self.restart_button.config(bg=hover_color))
        self.restart_button.bind('<Leave>', lambda e: self.restart_button.config(bg=main_color))

        self.quit_button = Button(self.frame, text="结束游戏", command=self.quit, **button_style)
        self.quit_button.pack(pady=20)
        self.quit_button.bind('<Enter>', lambda e: self.quit_button.config(bg=hover_color))
        self.quit_button.bind('<Leave>', lambda e: self.quit_button.config(bg=main_color))

    def restart(self):
        if self.on_restart:
            self.on_restart()
        self.master.destroy()

    def quit(self):
        if self.on_quit:
            self.on_quit()
        self.master.destroy()

if __name__ == "__main__":
    root = Tk()
    end_menu = EndMenu(root)
    root.mainloop() 