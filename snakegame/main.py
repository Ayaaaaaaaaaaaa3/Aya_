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
        
        # 游戏组件（延迟初始化，pygame初始化后再创建）
        self.snake = None
        self.food_system = None
        self.obstacles = None
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
        
        # 初始化关卡（不要在这里调用init_level，等pygame初始化后再调用）
        # self.init_level()
    
    def init_level(self):
        """初始化当前关卡"""
        # 先创建obstacles
        self.obstacles = Obstacle(self.current_level)
        
        # 先重置游戏组件
        self.snake = Snake()
        self.food_system = FoodSystem(self.current_level)
        
        # 再初始化关卡系统
        self.level_system = get_level(self.current_level, self)
        self.level_system.setup()
        
        # 重置游戏状态
        self.score = 0
        self.game_over = False
        self.win = False
        self.paused = False
        
        # 只在第十关创建BOSS
        if self.current_level == 10:
            self.boss = Boss(10, 10, GRID_SIZE, None)
            self.boss.set_mode("final")
        else:
            self.boss = None
        
        # 第四关蛇加速
        if self.current_level == 4:
            self.snake.speed = 2
    
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
        self.init_level()  # pygame初始化后再初始化关卡和游戏组件
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
            self._start_bg_surface = self.load_high_quality_image("assets/start_bg.jpg", (WINDOW_WIDTH, WINDOW_HEIGHT))
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
                        if self.snake is not None:
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
        if self.snake is None or self.food_system is None or self.obstacles is None:
            return
        # 更新蛇的位置
        self.snake.move()
        head = self.snake.body[0]
        
        # 检查撞墙/自撞
        if self.snake.check_collision(GRID_WIDTH, GRID_HEIGHT, [], None):
            # 检查是否处于无敌状态
            if hasattr(self.snake, 'special_effects') and "invincible" in self.snake.special_effects and self.snake.special_effects["invincible"] > 0:
                # 无敌期间穿墙，从对面出现
                head = self.snake.body[0]
                if head[0] < 0:
                    self.snake.body[0] = (GRID_WIDTH - 1, head[1])
                elif head[0] >= GRID_WIDTH:
                    self.snake.body[0] = (0, head[1])
                elif head[1] < 0:
                    self.snake.body[0] = (head[0], GRID_HEIGHT - 1)
                elif head[1] >= GRID_HEIGHT:
                    self.snake.body[0] = (head[0], 0)
            else:
                self.game_over = True
                return
        # 检查桥墩（像素级alpha判定）
        head_pixel = (head[0] * GRID_SIZE + GRID_SIZE // 2, head[1] * GRID_SIZE + GRID_SIZE // 2)
        dead = False
        for obs in self.obstacles.positions:
            if obs.get("type") == "bridge_pier":
                img = obs["image"]
                if obs.get("center_pixel"):
                    img_rect = img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                else:
                    x, y = obs["position"]
                    img_rect = img.get_rect(center=(x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2))
                if img_rect.collidepoint(head_pixel):
                    rel_x = head_pixel[0] - img_rect.left
                    rel_y = head_pixel[1] - img_rect.top
                    try:
                        alpha = img.get_at((int(rel_x), int(rel_y))).a
                    except IndexError:
                        alpha = 0
                    if alpha > 0:  # 只在图片不透明区域判定死亡
                        dead = True
                        break
        if dead:
            self.game_over = True
            return
        
        # 检查食物碰撞
        if self.food_system.check_food_collision(head):
            effect = self.food_system.apply_food_effect(self.snake)
            self.score += effect
            # 生成食物时排除所有障碍物（静态+动态）位置
            obstacle_positions = [obs["position"] for obs in self.obstacles.positions]
            moving_obstacle_positions = [obs["position"] for obs in self.obstacles.moving_obstacles]
            all_exclude_positions = obstacle_positions + moving_obstacle_positions
            
            # 第四关特殊处理：排除墙的位置
            if self.current_level == 4:
                wall_positions = [obs["position"] for obs in self.obstacles.positions if obs.get("type") == "wall"]
                all_exclude_positions += wall_positions
            
            if self.current_level == 10 and self.boss and self.boss.alive:
                boss_positions = [(self.boss.x, self.boss.y)]
                all_exclude_positions += boss_positions
                self.food_system.randomize_food_position(self.snake.body, all_exclude_positions)
            else:
                self.food_system.randomize_food_position(self.snake.body, all_exclude_positions)
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
        
        # 第五关水域减速逻辑
        if self.current_level == 5:
            in_water = False
            for zone in self.obstacles.hazard_zones:
                if zone["type"] == "water" and zone["active"]:
                    zx, zy = zone["position"]
                    dx = head[0] - zx
                    dy = head[1] - zy
                    if dx*dx + dy*dy <= (zone.get("radius",30)//GRID_SIZE)**2:
                        in_water = True
                        break
            if in_water:
                self.snake.slow_timer = 120  # 2秒减速
                self.snake.speed = 0.5
        # 每帧递减slow_timer，计时结束恢复速度
        if hasattr(self.snake, 'slow_timer') and self.snake.slow_timer > 0:
            self.snake.slow_timer -= 1
            if self.snake.slow_timer == 0:
                self.snake.speed = 1
        
        # 每帧递减无敌时间
        if hasattr(self.snake, 'special_effects') and "invincible" in self.snake.special_effects:
            if self.snake.special_effects["invincible"] > 0:
                self.snake.special_effects["invincible"] -= 1
        
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
        
        # 检查动态障碍物（如巡逻和尚）格子级判定
        for obs in self.obstacles.moving_obstacles:
            if obs.get("type") == "monk":
                if head == obs["position"]:
                    self.game_over = True
                    return
            elif obs.get("type") == "lightning" and obs["state"] == "active":
                # 闪电碰撞检测：格子级 + 像素级
                if head == obs["position"]:
                    self.game_over = True
                    return
                # 额外的像素级检测，因为闪电图片很大
                head_pixel = (head[0] * GRID_SIZE + GRID_SIZE // 2, head[1] * GRID_SIZE + GRID_SIZE // 2)
                x, y = obs["position"]
                img_rect = obs["image"].get_rect(
                    center=(x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2)
                )
                if img_rect.collidepoint(head_pixel):
                    # 检查像素是否不透明
                    rel_x = head_pixel[0] - img_rect.left
                    rel_y = head_pixel[1] - img_rect.top
                    try:
                        alpha = obs["image"].get_at((int(rel_x), int(rel_y))).a
                        if alpha > 0:  # 只在图片不透明区域判定死亡
                            self.game_over = True
                            return
                    except IndexError:
                        pass  # 如果坐标超出图片范围，忽略
        
        # 检查第四关墙壁碰撞
        if self.current_level == 4:
            for obs in self.obstacles.positions:
                if obs.get("type") == "wall":
                    if head == obs["position"]:
                        self.game_over = True
                        return
    
    def handle_special_item(self, item_type):
        """处理特殊物品效果"""
        if self.snake is None:
            return
        if item_type == "magic":
            self.snake.special_effects = getattr(self.snake, 'special_effects', {})
            self.snake.special_effects["invincible"] = 300  # 5秒无敌时间（60帧/秒 * 5秒）
        elif item_type == "rescue":
            self.score += 2
        elif item_type == "amulet":
            self.snake.special_effects = getattr(self.snake, 'special_effects', {})
            self.snake.special_effects["invincible"] = 300
            # 第十关护身符计数
            if self.current_level == 10:
                if not hasattr(self, 'amulet_eaten_count'):
                    self.amulet_eaten_count = 0
                self.amulet_eaten_count += 1
    
    def handle_hazard_effect(self, hazard_type):
        """处理危险区域效果"""
        if self.snake is None:
            return
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
        
        # 根据当前关卡加载背景
        if self.level_system and hasattr(self.level_system, 'get_background_image'):
            bg_image_path = self.level_system.get_background_image()
            if bg_image_path:
                # 动态加载关卡背景
                bg_key = f'_level{self.current_level}_bg_surface'
                if not hasattr(self, bg_key):
                    setattr(self, bg_key, self.load_high_quality_image(bg_image_path, (WINDOW_WIDTH, WINDOW_HEIGHT)))
                bg_surface = getattr(self, bg_key)
                if bg_surface:
                    self.screen.blit(bg_surface, (0, 0))
                else:
                    self.screen.fill(BLACK)
            else:
                self.screen.fill(BLACK)
        else:
            self.screen.fill(BLACK)
        
        # 渲染障碍物
        if self.obstacles is not None:
            self.obstacles.render(self.screen)
        
        # 渲染食物
        if self.food_system is not None:
            self.food_system.render_food(self.screen)
        
        # 渲染蛇
        if self.snake is not None:
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
        food_type = getattr(self.food_system, 'food_type', 'green_fruit') if self.food_system is not None else 'green_fruit'
        food_name = food_type_map.get(food_type, "食物")
        food_count = self.food_system.food_count if self.food_system is not None else 0
        food_count_text = self.font.render(f"{food_name}: {food_count}", True, WHITE)
        self.screen.blit(food_count_text, (10, 130))
        
        # 第十关显示护身符数量
        if self.current_level == 10 and self.obstacles is not None:
            # 累计吃掉的护身符数量
            if not hasattr(self, 'amulet_eaten_count'):
                self.amulet_eaten_count = 0
            amulet_text = self.font.render(f"护身符: {self.amulet_eaten_count}", True, (255, 215, 0))  # 金色
            self.screen.blit(amulet_text, (10, 170))
        
        # 暂停状态
        if self.paused:
            pause_text = self.font.render("游戏暂停 - 按ESC继续", True, YELLOW)
            text_rect = pause_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
            self.screen.blit(pause_text, text_rect)
        
        # 游戏结束
        if self.game_over:
            # 加载并显示结束背景图片
            if not hasattr(self, '_end_bg_surface'):
                self._end_bg_surface = self.load_high_quality_image("assets/end_bg.jpg", (WINDOW_WIDTH, WINDOW_HEIGHT))
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

    def load_high_quality_image(self, image_path, target_size):
        """加载高质量图片，使用更好的缩放算法提高清晰度"""
        try:
            import pygame
            import os
            if os.path.exists(image_path):
                # 加载原始图片
                original_img = pygame.image.load(image_path).convert_alpha()
                
                # 获取原始尺寸
                original_size = original_img.get_size()
                
                # 计算缩放比例
                scale_x = target_size[0] / original_size[0]
                scale_y = target_size[1] / original_size[1]
                
                # 如果原始图片比目标尺寸大很多，使用多步缩放
                if scale_x < 0.5 or scale_y < 0.5:
                    # 多步缩放以获得更好的质量
                    current_img = original_img
                    current_size = original_size
                    
                    # 逐步缩小，每次最多缩小一半
                    while current_size[0] > target_size[0] * 1.5 or current_size[1] > target_size[1] * 1.5:
                        # 计算下一步的尺寸
                        next_width = max(int(current_size[0] * 0.7), int(target_size[0] * 1.5))
                        next_height = max(int(current_size[1] * 0.7), int(target_size[1] * 1.5))
                        next_size = (next_width, next_height)
                        
                        # 使用smoothscale进行高质量缩放
                        current_img = pygame.transform.smoothscale(current_img, next_size)
                        current_size = next_size
                    
                    # 最后缩放到目标尺寸
                    final_img = pygame.transform.smoothscale(current_img, target_size)
                else:
                    # 直接使用smoothscale缩放到目标尺寸
                    final_img = pygame.transform.smoothscale(original_img, target_size)
                
                return final_img
            else:
                return None
        except Exception as e:
            print(f"图片加载失败: {image_path}, 错误: {str(e)}")
            return None

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