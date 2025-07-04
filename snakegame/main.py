"""
白蛇传贪吃蛇游戏主函数
整合所有游戏组件，包括UI界面、游戏逻辑、关卡系统等
"""
import pygame
import sys
import os
from tkinter import Tk, messagebox
from PIL import Image, ImageTk

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
from UI.end_menu import EndMenu

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
        
        # 新增状态
        self.state = "start_menu"  # 新增状态：start_menu, playing, level_select, skin_select, record
        
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
    
    def show_pygame_menu_loop(self):
        import pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("白蛇贪吃劫")
        self.font = self.load_chinese_font(24)
        self.clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.handle_events()
            self.render()
            if self.state == "playing":
                self.update_game()
            if self.clock:
                self.clock.tick(FPS)

    def render(self):
        if self.state == "start_menu":
            self.render_start_menu()
        elif self.state == "level_select":
            self.render_level_select()
        elif self.state == "skin_select":
            self.render_skin_select()
        elif self.state == "record":
            self.render_record()
        elif self.state == "playing":
            self.render_game()
        # 可扩展其它状态

    def render_start_menu(self):
        import pygame
        if self.screen is None or self.font is None:
            return
        # 背景
        if not hasattr(self, '_start_bg_surface'):
            import os
            if os.path.exists("assets/start_bg.jpg"):
                self._start_bg_surface = pygame.image.load("assets/start_bg.jpg").convert()
                self._start_bg_surface = pygame.transform.scale(self._start_bg_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
            else:
                self._start_bg_surface = None
        if self._start_bg_surface:
            self.screen.blit(self._start_bg_surface, (0, 0))
        else:
            self.screen.fill((34, 85, 96))
        # 按钮参数
        btn_w, btn_h = 200, 50
        btn_color = (34, 85, 96)
        btn_hover = (110, 193, 228)
        font_color = (255, 255, 255)
        font = self.font
        # 右下角布局
        margin = 30
        x = WINDOW_WIDTH - btn_w - margin
        y0 = WINDOW_HEIGHT - (btn_h + 15) * 4 - margin
        btns = ["开始游戏", "选择关卡", "选择皮肤", "战绩记录"]
        self.menu_btn_rects = []
        mx, my = pygame.mouse.get_pos()
        for i, text in enumerate(btns):
            y = y0 + i * (btn_h + 15)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            color = btn_hover if rect.collidepoint(mx, my) else btn_color
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            btn_text = font.render(text, True, font_color)
            text_rect = btn_text.get_rect(center=rect.center)
            self.screen.blit(btn_text, text_rect)
            self.menu_btn_rects.append(rect)
        pygame.display.flip()

    def render_level_select(self):
        import pygame
        if self.screen is None or self.font is None:
            return
        if hasattr(self, '_start_bg_surface') and self._start_bg_surface:
            self.screen.blit(self._start_bg_surface, (0, 0))
        else:
            self.screen.fill((34, 85, 96))
        title = self.font.render("请选择关卡", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH - 300, 40))
        btn_w, btn_h = 120, 38
        btn_color = (34, 85, 96)
        btn_hover = (110, 193, 228)
        font_color = (255, 255, 255)
        margin = 30
        x = WINDOW_WIDTH - btn_w - margin
        y0 = 80
        gap = 6
        self.level_btn_rects = []
        mx, my = pygame.mouse.get_pos()
        for i in range(10):
            y = y0 + i * (btn_h + gap)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            color = btn_hover if rect.collidepoint(mx, my) else btn_color
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            btn_text = self.font.render(f"关卡 {i+1}", True, font_color)
            text_rect = btn_text.get_rect(center=rect.center)
            self.screen.blit(btn_text, text_rect)
            self.level_btn_rects.append(rect)
        # 返回按钮
        back_rect = pygame.Rect(x, y0 + 10 * (btn_h + gap) + 10, btn_w, btn_h)
        color = btn_hover if back_rect.collidepoint(mx, my) else btn_color
        pygame.draw.rect(self.screen, color, back_rect, border_radius=8)
        back_text = self.font.render("返回", True, font_color)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)
        self.level_back_rect = back_rect
        pygame.display.flip()

    def render_skin_select(self):
        import pygame
        if self.screen is None or self.font is None:
            return
        if hasattr(self, '_start_bg_surface') and self._start_bg_surface:
            self.screen.blit(self._start_bg_surface, (0, 0))
        else:
            self.screen.fill((34, 85, 96))
        title = self.font.render("请选择皮肤", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH - 300, 80))
        skins = ["皮肤1", "皮肤2", "皮肤3", "皮肤4"]
        btn_w, btn_h = 120, 40
        btn_color = (34, 85, 96)
        btn_hover = (110, 193, 228)
        font_color = (255, 255, 255)
        margin = 30
        x = WINDOW_WIDTH - btn_w - margin
        y0 = 150
        self.skin_btn_rects = []
        mx, my = pygame.mouse.get_pos()
        for i, skin in enumerate(skins):
            y = y0 + i * (btn_h + 10)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            color = btn_hover if rect.collidepoint(mx, my) else btn_color
            pygame.draw.rect(self.screen, color, rect, border_radius=8)
            btn_text = self.font.render(skin, True, font_color)
            text_rect = btn_text.get_rect(center=rect.center)
            self.screen.blit(btn_text, text_rect)
            self.skin_btn_rects.append(rect)
        # 返回按钮
        back_rect = pygame.Rect(x, y0 + 5 * (btn_h + 10), btn_w, btn_h)
        color = btn_hover if back_rect.collidepoint(mx, my) else btn_color
        pygame.draw.rect(self.screen, color, back_rect, border_radius=8)
        back_text = self.font.render("返回", True, font_color)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)
        self.skin_back_rect = back_rect
        pygame.display.flip()

    def render_record(self):
        import pygame
        if self.screen is None or self.font is None:
            return
        if hasattr(self, '_start_bg_surface') and self._start_bg_surface:
            self.screen.blit(self._start_bg_surface, (0, 0))
        else:
            self.screen.fill((34, 85, 96))
        title = self.font.render("战绩记录", True, (255, 255, 255))
        self.screen.blit(title, (WINDOW_WIDTH - 300, 80))
        records = self.record_system.scores[-10:] if hasattr(self.record_system, 'scores') else []
        for i, score in enumerate(records):
            text = self.font.render(f"{i+1}. 分数: {score}", True, (255, 255, 255))
            self.screen.blit(text, (WINDOW_WIDTH - 300, 140 + i * 40))
        btn_w, btn_h = 120, 40
        btn_color = (34, 85, 96)
        btn_hover = (110, 193, 228)
        font_color = (255, 255, 255)
        margin = 30
        x = WINDOW_WIDTH - btn_w - margin
        y = WINDOW_HEIGHT - btn_h - margin
        mx, my = pygame.mouse.get_pos()
        back_rect = pygame.Rect(x, y, btn_w, btn_h)
        color = btn_hover if back_rect.collidepoint(mx, my) else btn_color
        pygame.draw.rect(self.screen, color, back_rect, border_radius=8)
        back_text = self.font.render("返回", True, font_color)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)
        self.record_back_rect = back_rect
        pygame.display.flip()

    def handle_events(self):
        import pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.state == "start_menu":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if hasattr(self, 'menu_btn_rects'):
                        if self.menu_btn_rects[0].collidepoint(mx, my):
                            self.state = "playing"
                            self.init_level()
                        elif self.menu_btn_rects[1].collidepoint(mx, my):
                            self.state = "level_select"
                        elif self.menu_btn_rects[2].collidepoint(mx, my):
                            self.state = "skin_select"
                        elif self.menu_btn_rects[3].collidepoint(mx, my):
                            self.state = "record"
            elif self.state == "level_select":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    for i, rect in enumerate(self.level_btn_rects):
                        if rect.collidepoint(mx, my):
                            self.current_level = i + 1
                            self.state = "playing"
                            self.init_level()
                            return
                    if self.level_back_rect.collidepoint(mx, my):
                        self.state = "start_menu"
            elif self.state == "skin_select":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    for i, rect in enumerate(self.skin_btn_rects):
                        if rect.collidepoint(mx, my):
                            self.selected_skin = f"皮肤{i+1}"
                            self.state = "start_menu"
                            return
                    if self.skin_back_rect.collidepoint(mx, my):
                        self.state = "start_menu"
            elif self.state == "record":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if hasattr(self, 'record_back_rect') and self.record_back_rect.collidepoint(mx, my):
                        self.state = "start_menu"
            elif self.state == "playing":
                if event.type == pygame.KEYDOWN:
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
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
                    mx, my = event.pos
                    if hasattr(self, 'button_restart_rect') and self.button_restart_rect.collidepoint(mx, my):
                        self.state = "start_menu"
                        self.game_over = False
                        self.win = False
                    elif hasattr(self, 'button_quit_rect') and self.button_quit_rect.collidepoint(mx, my):
                        self.running = False
                        import pygame
                        pygame.quit()
                        import sys
                        sys.exit()
    
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
    
    def render_game(self):
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
        food_type_map = {
            "green_fruit": "青蛇果",
            "lotus_fruit": "莲花果",
            "ganoderma": "灵芝果",
            "herb": "仙草果",
            "water_fruit": "水灵果",
            "magic_fruit": "法力果",
            "vine_fruit": "青藤果",
            "illusion_fruit": "幻境果",
            "lightning_fruit": "雷电果",
            "bead_fruit": "佛珠果"
        }
        food_type = getattr(self.food_system, 'food_type', 'green_fruit')
        food_name = food_type_map.get(food_type, "食物")
        food_count_text = self.font.render(f"{food_name}: {self.food_system.food_count}", True, WHITE)
        self.screen.blit(food_count_text, (10, 130))
        
        # 暂停状态
        if self.paused:
            pause_text = self.font.render("游戏暂停 - 按ESC继续", True, YELLOW)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(pause_text, text_rect)
        
        # 游戏结束
        if self.game_over:
            # 加载并显示结束背景图片
            if not hasattr(self, '_end_bg_surface'):
                import pygame
                import os
                if os.path.exists("assets/end_bg.jpg"):
                    self._end_bg_surface = pygame.image.load("assets/end_bg.jpg").convert()
                    self._end_bg_surface = pygame.transform.scale(self._end_bg_surface, (WINDOW_WIDTH, WINDOW_HEIGHT))
                else:
                    self._end_bg_surface = None
            if self._end_bg_surface:
                self.screen.blit(self._end_bg_surface, (0, 0))
            game_over_text = self.font.render("游戏结束", True, RED)
            text_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 60))
            self.screen.blit(game_over_text, text_rect)
            # 画按钮
            self.draw_end_buttons()
        
        # 胜利
        if self.win:
            win_text = self.font.render("恭喜通关！", True, GREEN)
            text_rect = win_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(win_text, text_rect)
    
    def draw_end_buttons(self):
        if self.screen is None or self.font is None:
            return
        # 按钮参数
        btn_w, btn_h = 200, 60
        btn_color = (34, 85, 96)
        btn_hover = (110, 193, 228)
        font_color = (255, 255, 255)
        font = self.font
        center_x = WINDOW_WIDTH // 2
        y1 = WINDOW_HEIGHT // 2 + 10
        y2 = y1 + btn_h + 20
        # 获取鼠标位置
        import pygame
        mx, my = pygame.mouse.get_pos()
        # 重新开始按钮
        self.button_restart_rect = pygame.Rect(center_x - btn_w//2, y1, btn_w, btn_h)
        restart_color = btn_hover if self.button_restart_rect.collidepoint(mx, my) else btn_color
        pygame.draw.rect(self.screen, restart_color, self.button_restart_rect, border_radius=12)
        restart_text = font.render("重新开始", True, font_color)
        text_rect = restart_text.get_rect(center=self.button_restart_rect.center)
        self.screen.blit(restart_text, text_rect)
        # 结束游戏按钮
        self.button_quit_rect = pygame.Rect(center_x - btn_w//2, y2, btn_w, btn_h)
        quit_color = btn_hover if self.button_quit_rect.collidepoint(mx, my) else btn_color
        pygame.draw.rect(self.screen, quit_color, self.button_quit_rect, border_radius=12)
        quit_text = font.render("结束游戏", True, font_color)
        text_rect = quit_text.get_rect(center=self.button_quit_rect.center)
        self.screen.blit(quit_text, text_rect)
    
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
        import pygame
        pygame.quit()
        import sys
        sys.exit()
    
    def run(self):
        self.state = "start_menu"
        self.show_pygame_menu_loop()

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