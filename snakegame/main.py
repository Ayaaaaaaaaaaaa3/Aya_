"""
白蛇传贪吃蛇游戏主函数
整合所有游戏组件，包括UI界面、游戏逻辑、关卡系统等
"""
import pygame
import sys
import os
from tkinter import Tk, messagebox

# 导入游戏组件
from config import *
from snake import Snake
from food import FoodSystem
from obstacles import Obstacle
from boss import Boss
from 基础机制 import get_level
from UI.start_menu import StartMenu
from UI.level_select import LevelSelect
from UI.skin_select import SkinSelect
from UI.record import Record

class Game:
    def __init__(self):
        # 游戏状态
        self.running = False
        self.paused = False
        self.game_over = False
        self.win = False
        self.current_level = 1
        self.selected_skin = "皮肤1"
        
        # 游戏组件
        self.snake = Snake()
        self.food_system = FoodSystem(self.current_level)
        self.obstacles = Obstacle(self.current_level)
        self.boss = None
        self.level_system = None
        
        # UI组件
        self.record_system = Record()
        self.tk_root = None
        self.start_menu = None
        
        # 游戏数据
        self.score = 0
        self.target_score = 10
        self.moving_obstacles = []
        self.flood_zones = []
        self.fog_areas = []
        
        # Pygame组件（延迟初始化）
        self.screen = None
        self.clock = None
        self.font = None  # 中文字体
        
        # 初始化关卡
        self.init_level()
    
    def init_level(self):
        """初始化当前关卡"""
        # 先创建obstacles，再初始化关卡系统
        self.obstacles = Obstacle(self.current_level)
        
        # 初始化关卡系统
        self.level_system = get_level(self.current_level, self)
        self.level_system.setup()
        
        # 重置游戏组件
        self.snake = Snake()
        self.food_system = FoodSystem(self.current_level)
        
        # 重置游戏状态
        self.score = 0
        self.game_over = False
        self.win = False
        self.paused = False
        
        # 特殊关卡处理
        if self.current_level == 10:
            self.boss = Boss(10, 10, GRID_SIZE, None)
            self.boss.set_mode("final")
    
    def load_chinese_font(self, size=24):
        """加载支持中文的字体"""
        try:
            # 优先尝试微软雅黑
            return pygame.font.Font("C:/Windows/Fonts/msyh.ttc", size)
        except:
            try:
                # 尝试宋体
                return pygame.font.Font("C:/Windows/Fonts/simsun.ttc", size)
            except:
                try:
                    # 尝试系统默认字体
                    return pygame.font.SysFont("arial", size)
                except:
                    # 最后使用pygame默认字体
                    return pygame.font.Font(None, size)
    
    def show_start_menu(self):
        """显示开始菜单"""
        self.tk_root = Tk()
        self.start_menu = StartMenu(self.tk_root)
        # 绑定按钮事件
        self.start_menu.skin_button.config(command=self.show_skin_select)
        self.start_menu.level_button.config(command=self.show_level_select)
        self.start_menu.start_button.config(command=self.start_game)
        self.start_menu.record_button.config(command=self.show_records)
        self.tk_root.mainloop()  # 阻塞，直到窗口销毁
    
    def show_skin_select(self):
        """显示皮肤选择界面"""
        if self.tk_root is not None:
            # 添加淡出效果
            self.tk_root.attributes('-alpha', 0.8)
            self.tk_root.after(100, lambda: self.tk_root.attributes('-alpha', 0.6) if self.tk_root else None)
            self.tk_root.after(200, lambda: self.tk_root.destroy() if self.tk_root else None)
            self.tk_root = None
        self.tk_root = Tk()
        skin_select = SkinSelect(self.tk_root)
        def confirm_and_back():
            self.selected_skin = skin_select.selected_skin.get()
            if self.tk_root is not None:
                self.tk_root.destroy()
                self.tk_root = None
            self.show_start_menu()
        def back_and_menu():
            if self.tk_root is not None:
                self.tk_root.destroy()
                self.tk_root = None
            self.show_start_menu()
        skin_select.confirm_button.config(command=confirm_and_back)
        skin_select.back_button.config(command=back_and_menu)
        self.tk_root.mainloop()
    
    def show_level_select(self):
        """显示关卡选择界面"""
        if self.tk_root is not None:
            # 添加淡出效果
            self.tk_root.attributes('-alpha', 0.8)
            self.tk_root.after(100, lambda: self.tk_root.attributes('-alpha', 0.6) if self.tk_root else None)
            self.tk_root.after(200, lambda: self.tk_root.destroy() if self.tk_root else None)
            self.tk_root = None
        self.tk_root = Tk()
        level_select = LevelSelect(self.tk_root)
        def select_level_and_start(level):
            self.current_level = level
            if self.tk_root is not None:
                self.tk_root.destroy()
                self.tk_root = None
            self.start_game()
        def back_to_menu():
            if self.tk_root is not None:
                self.tk_root.destroy()
                self.tk_root = None
            self.show_start_menu()
        for i, button in enumerate(level_select.level_buttons):
            button.config(command=lambda level=i+1: select_level_and_start(level))
        level_select.back_button.config(command=back_to_menu)
        self.tk_root.mainloop()
    
    def show_records(self):
        """显示战绩记录"""
        records_text = self.record_system.display_records()
        messagebox.showinfo("战绩记录", records_text)
    
    def start_game(self):
        """开始游戏"""
        if self.tk_root is not None:
            self.tk_root.withdraw()  # 隐藏而不是销毁
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("白蛇贪吃劫")
        # 置顶Pygame窗口
        try:
            import ctypes
            hwnd = pygame.display.get_wm_info()['window']
            ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
        except Exception as e:
            print("置顶失败：", e)
        self.font = self.load_chinese_font(24)
        self.clock = pygame.time.Clock()
        self.init_level()
        self.running = True
        self.game_loop()  # 只运行Pygame主循环
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif not self.paused and not self.game_over:
                    if event.key == pygame.K_UP:
                        self.snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction((1, 0))
    
    def update_game(self):
        """更新游戏逻辑"""
        if self.paused or self.game_over:
            return
        
        # 更新蛇的位置
        self.snake.move()
        head = self.snake.body[0]
        
        # 检查撞墙/自撞/障碍物
        if self.snake.check_collision(GRID_WIDTH, GRID_HEIGHT, [obs["position"] for obs in self.obstacles.positions]):
            self.game_over = True
            return
        
        # 检查食物碰撞
        if self.food_system.check_food_collision(head):
            effect = self.food_system.apply_food_effect(self.snake)
            self.score += effect
            self.food_system.randomize_food_position(self.snake.body)
            
            # 特殊关卡处理
            if self.current_level == 10 and effect == 5 and self.boss:
                self.boss.set_weak(True)
        
        # 检查特殊物品碰撞
        special_item = self.obstacles.check_special_item_collision(head)
        if special_item:
            self.handle_special_item(special_item)
        
        # 检查危险区域效果
        hazard_effect = self.obstacles.check_hazard_effect(head)
        if hazard_effect:
            self.handle_hazard_effect(hazard_effect)
        
        # 更新障碍物
        self.obstacles.update()
        
        # 更新BOSS
        if self.boss and self.boss.alive:
            self.boss.move(GRID_WIDTH, GRID_HEIGHT, 
                          [obs["position"] for obs in self.obstacles.positions],
                          head)
            if self.boss.check_ball_hit(self.snake.body):
                self.game_over = True
                return
        
        # 更新关卡特殊机制
        if self.level_system:
            self.level_system.update()
        
        # 检查关卡完成
        if self.food_system.is_level_complete():
            if self.current_level == 10:
                self.win = True
            else:
                self.next_level()
    
    def handle_special_item(self, item_type):
        """处理特殊物品效果"""
        if item_type == "magic":
            self.snake.special_effects = getattr(self.snake, 'special_effects', {})
            self.snake.special_effects["invincible"] = 100
        elif item_type == "rescue":
            self.score += 2
        elif item_type == "amulet":
            self.snake.special_effects = getattr(self.snake, 'special_effects', {})
            self.snake.special_effects["invincible"] = 300
    
    def handle_hazard_effect(self, hazard_type):
        """处理危险区域效果"""
        if hazard_type == "water":
            # 减速效果可以通过调整游戏速度实现
            pass
        elif hazard_type == "lightning_zone":
            if not hasattr(self.snake, 'special_effects') or "invincible" not in self.snake.special_effects:
                self.game_over = True
    
    def next_level(self):
        """进入下一关"""
        self.current_level += 1
        if self.current_level <= MAX_LEVEL:
            self.init_level()
        else:
            self.win = True
    
    def restart_game(self):
        """重新开始游戏"""
        self.current_level = 1
        self.init_level()
    
    def render(self):
        """渲染游戏画面"""
        if self.screen is None:
            return
            
        self.screen.fill(BLACK)
        
        # 渲染障碍物
        self.obstacles.render(self.screen)
        
        # 渲染食物
        self.food_system.render_food(self.screen)
        
        # 渲染蛇
        self.snake.render(self.screen, GRID_SIZE)
        
        # 渲染BOSS
        if self.boss and self.boss.alive:
            self.boss.draw(self.screen)
        
        # 渲染UI
        self.render_ui()
        
        pygame.display.flip()
    
    def show_game_over_dialog(self):
        import tkinter as tk
        from tkinter import ttk
        
        dialog = tk.Toplevel()
        dialog.title("游戏结束")
        dialog.geometry("300x180")
        dialog.resizable(False, False)
        dialog.grab_set()  # 模态窗口
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 150
        y = (dialog.winfo_screenheight() // 2) - 90
        dialog.geometry(f"300x180+{x}+{y}")
        
        label = ttk.Label(dialog, text="游戏结束", font=("微软雅黑", 18))
        label.pack(pady=30)
        
        def restart():
            dialog.destroy()
            self.running = False  # 先安全退出主循环
            self.restart_game()
            self.running = True
            self.game_loop()
            
        def quit_game():
            dialog.destroy()
            self.running = False  # 先安全退出主循环
            pygame.quit()
            sys.exit()
        
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        restart_btn = ttk.Button(btn_frame, text="重新开始", command=restart, width=12)
        restart_btn.grid(row=0, column=0, padx=10)
        quit_btn = ttk.Button(btn_frame, text="结束游戏", command=quit_game, width=12)
        quit_btn.grid(row=0, column=1, padx=10)
        
        dialog.wait_window()
    
    def render_ui(self):
        """渲染用户界面"""
        if self.screen is None or self.font is None:
            return
            
        # 显示分数
        score_text = self.font.render(f"分数: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # 显示关卡
        level_text = self.font.render(f"关卡: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (10, 50))
        
        # 显示目标
        target_text = self.font.render(f"目标: {self.target_score}", True, WHITE)
        self.screen.blit(target_text, (10, 90))
        
        # 显示食物计数
        food_count_text = self.font.render(f"食物: {self.food_system.food_count}", True, WHITE)
        self.screen.blit(food_count_text, (10, 130))
        
        # 暂停状态
        if self.paused:
            pause_text = self.font.render("游戏暂停 - 按ESC继续", True, YELLOW)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(pause_text, text_rect)
        
        # 游戏结束
        if self.game_over:
            game_over_text = self.font.render("游戏结束", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(game_over_text, text_rect)
            # 弹出交互窗口（只弹一次）
            if not hasattr(self, '_game_over_dialog_shown'):
                self._game_over_dialog_shown = True
                pygame.display.update()
                self.show_game_over_dialog()
        
        # 胜利
        if self.win:
            win_text = self.font.render("恭喜通关！", True, GREEN)
            text_rect = win_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(win_text, text_rect)
        
        # 如果不是game_over，重置弹窗标志
        if not self.game_over and hasattr(self, '_game_over_dialog_shown'):
            del self._game_over_dialog_shown
    
    def game_loop(self):
        """游戏主循环"""
        while self.running:
            self.handle_events()
            self.update_game()
            self.render()
            if self.clock:
                self.clock.tick(FPS)
        # 游戏结束，保存记录
        if self.score > 0:
            self.record_system.add_score(self.score)
        pygame.quit()
        if self.tk_root is not None:
            self.tk_root.deiconify()  # 恢复Tk窗口
        self.show_start_menu()
    
    def run(self):
        """运行游戏"""
        self.show_start_menu()

def main():
    """主函数"""
    # 创建assets目录
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists("assets/food"):
        os.makedirs("assets/food")
    if not os.path.exists("assets/obstacles"):
        os.makedirs("assets/obstacles")
    
    # 创建并运行游戏
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 