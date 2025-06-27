import pygame
import random
import sys
import time
import math

# 初始化pygame
pygame.init()

# 确保中文能正常显示
pygame.font.init()
font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], 24)

# 游戏常量
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# 方向定义
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 饱和度高的淡蓝色
BG_COLOR = (100, 180, 255)  # 更鲜艳的淡蓝色

# 食物类型
FOOD_NORMAL = 'normal'
FOOD_SPEEDUP = 'speedup'
FOOD_SLOWDOWN = 'slowdown'
FOOD_SHRINK = 'shrink'
FOOD_INVINCIBLE = 'invincible'
FOOD_REVERSE = 'reverse'
FOOD_TYPES = [FOOD_NORMAL, FOOD_SPEEDUP, FOOD_SLOWDOWN, FOOD_SHRINK, FOOD_INVINCIBLE, FOOD_REVERSE]
FOOD_COLORS = {
    FOOD_NORMAL: (255, 80, 80),
    FOOD_SPEEDUP: (255, 200, 0),
    FOOD_SLOWDOWN: (0, 200, 255),
    FOOD_SHRINK: (180, 0, 255),
    FOOD_INVINCIBLE: (0, 255, 120),
    FOOD_REVERSE: (255, 120, 0),
}

# 卡通云朵和草地
CLOUD_COLOR = (255, 255, 255, 180)
GRASS_COLOR = (80, 200, 80)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        """重置蛇的状态到初始"""
        self.length = 3
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = RIGHT
        self.last_direction = self.direction
        self.score = 0
        self.color = GREEN
        
    def get_head_position(self):
        """获取蛇头位置"""
        return self.positions[0]
    
    def turn(self, new_direction):
        """改变蛇的方向，但不能直接反向"""
        if (new_direction[0] * -1, new_direction[1] * -1) == self.last_direction:
            return
        self.direction = new_direction
    
    def move(self):
        """移动蛇并处理碰撞"""
        head = self.get_head_position()
        x, y = self.direction
        new_x = head[0] + x
        new_y = head[1] + y
        new_head = (new_x, new_y)
        # 检查是否撞到边界
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return 'hit_wall'
        # 检查是否撞到自己
        if new_head in self.positions[2:]:
            self.reset()
            return False
        else:
            self.positions.insert(0, new_head)
            # 如果长度超过当前长度，移除尾部
            if len(self.positions) > self.length:
                self.positions.pop()
            self.last_direction = self.direction
            return True
    
    def draw(self, surface):
        """在屏幕上绘制蛇"""
        for i, p in enumerate(self.positions):
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            # 蛇头更亮
            color = (0, 255, 100) if i == 0 else self.color
            pygame.draw.rect(surface, color, rect, border_radius=8)
            pygame.draw.rect(surface, WHITE, rect, 1, border_radius=8)

class Obstacle:
    def __init__(self, positions=None):
        self.positions = positions or []
        self.color = (40, 40, 40)  # 更深的灰色
    def randomize(self, snake_positions, food_position, count=8):
        self.positions = []
        while len(self.positions) < count:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in self.positions and pos not in snake_positions and pos != food_position:
                self.positions.append(pos)
    def draw(self, surface):
        for p in self.positions:
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, rect, border_radius=4)
            pygame.draw.rect(surface, WHITE, rect, 3, border_radius=4)  # 更粗的白色边框
            # 在障碍物中央画一个白色X
            cx, cy = rect.center
            offset = GRID_SIZE // 3
            pygame.draw.line(surface, WHITE, (cx - offset, cy - offset), (cx + offset, cy + offset), 2)
            pygame.draw.line(surface, WHITE, (cx - offset, cy + offset), (cx + offset, cy - offset), 2)

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.type = FOOD_NORMAL
        self.color = FOOD_COLORS[self.type]
        self.randomize_position([])
    def randomize_position(self, obstacles):
        while True:
            pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if pos not in obstacles:
                self.position = pos
                break
        self.type = random.choices(FOOD_TYPES, weights=[60,10,10,8,6,6])[0]
        self.color = FOOD_COLORS[self.type]
    def draw(self, surface):
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        center = (rect.x + GRID_SIZE // 2, rect.y + GRID_SIZE // 2)
        pygame.draw.circle(surface, self.color, center, GRID_SIZE // 2 - 2)
        pygame.draw.circle(surface, WHITE, center, GRID_SIZE // 2 - 2, 2)

# 新增：绘制带半透明背景的文本
def draw_text_with_bg(surface, text, font, pos, text_color, bg_color, padding=8, alpha=180):
    txt_surf = font.render(text, True, text_color)
    bg_surf = pygame.Surface((txt_surf.get_width() + padding * 2, txt_surf.get_height() + padding * 2), pygame.SRCALPHA)
    bg_surf.fill((*bg_color, alpha))
    bg_rect = bg_surf.get_rect(center=pos)
    surface.blit(bg_surf, bg_rect)
    surface.blit(txt_surf, (bg_rect.x + padding, bg_rect.y + padding))

def draw_cartoon_bg(surface):
    # 画云朵
    cloud_shapes = [
        # (x, y, w, h)
        (80, 60, 90, 40), (200, 100, 60, 30), (350, 50, 100, 45),
        (600, 80, 80, 35), (700, 40, 70, 30), (500, 120, 60, 25)
    ]
    for x, y, w, h in cloud_shapes:
        cloud = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud, CLOUD_COLOR, (0, 0, w, h))
        surface.blit(cloud, (x, y))
    # 画草地（底部波浪）
    grass_height = 60
    points = []
    for i in range(SCREEN_WIDTH+1):
        wave = math.sin(i/60.0) * 10 + math.cos(i/30.0) * 5
        points.append((i, SCREEN_HEIGHT - grass_height + wave))
    points += [(SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
    pygame.draw.polygon(surface, GRASS_COLOR, points)

def main():
    """主游戏函数"""
    # 设置游戏窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("贪吃蛇游戏原型")
    
    # 创建时钟控制游戏速度
    clock = pygame.time.Clock()
    
    # 创建游戏对象
    snake = Snake()
    food = Food()
    obstacle = Obstacle()
    speed = 10
    invincible = False
    invincible_end_time = 0
    reverse = False
    reverse_end_time = 0
    last_eat_time = time.time()
    combo = 0
    level = 1
    
    # 初始障碍物
    obstacle.randomize(snake.positions, food.position, count=4)
    
    # 游戏状态: start, playing, game_over
    game_state = "start"
    running = True
    
    # 新增大号字体
    big_font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], 48)
    
    while running:
        clock.tick(speed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "start":
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        snake.reset()
                        food.randomize_position(obstacle.positions)
                elif game_state == "playing":
                    if reverse:
                        # 方向反转
                        if event.key == pygame.K_UP:
                            snake.turn(DOWN)
                        elif event.key == pygame.K_DOWN:
                            snake.turn(UP)
                        elif event.key == pygame.K_LEFT:
                            snake.turn(RIGHT)
                        elif event.key == pygame.K_RIGHT:
                            snake.turn(LEFT)
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                    else:
                        if event.key == pygame.K_UP:
                            snake.turn(UP)
                        elif event.key == pygame.K_DOWN:
                            snake.turn(DOWN)
                        elif event.key == pygame.K_LEFT:
                            snake.turn(LEFT)
                        elif event.key == pygame.K_RIGHT:
                            snake.turn(RIGHT)
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                elif game_state == "game_over":
                    if event.key == pygame.K_r:
                        game_state = "playing"
                        snake.reset()
                        speed = 10
                        invincible = False
                        invincible_end_time = 0
                        reverse = False
                        reverse_end_time = 0
                        combo = 0
                        level = 1
                        last_eat_time = time.time()
                        obstacle.randomize(snake.positions, food.position, count=4)
                        food.randomize_position(obstacle.positions)
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if game_state == "playing":
            move_result = snake.move()
            # 蛇碰到障碍物
            if snake.get_head_position() in obstacle.positions and not invincible:
                game_state = "game_over"
            elif move_result == 'hit_wall' and not invincible:
                game_state = "game_over"
            elif move_result is False:
                game_state = "game_over"
            # 检查是否吃到食物
            if snake.get_head_position() == food.position:
                last_eat_time = time.time()
                combo += 1
                if food.type == FOOD_NORMAL:
                    snake.length += 1
                    snake.score += 1
                elif food.type == FOOD_SPEEDUP:
                    speed = min(25, speed + 3)
                    snake.length += 1
                    snake.score += 2
                elif food.type == FOOD_SLOWDOWN:
                    speed = max(5, speed - 3)
                    snake.length += 1
                    snake.score += 2
                elif food.type == FOOD_SHRINK:
                    if snake.length > 3:
                        snake.length -= 1
                    snake.score += 2
                elif food.type == FOOD_INVINCIBLE:
                    invincible = True
                    invincible_end_time = time.time() + 5
                    snake.length += 1
                    snake.score += 3
                elif food.type == FOOD_REVERSE:
                    reverse = True
                    reverse_end_time = time.time() + 5
                    snake.length += 1
                    snake.score += 3
                # 连击奖励
                if combo >= 3:
                    snake.score += combo
                # 关卡提升
                if snake.score >= level * 10:
                    level += 1
                    obstacle.randomize(snake.positions, food.position, count=4+level)
                food.randomize_position(obstacle.positions)
            # 限时挑战
            if time.time() - last_eat_time > 12:
                game_state = "game_over"
            # 无敌/反向计时
            if invincible and time.time() > invincible_end_time:
                invincible = False
            if reverse and time.time() > reverse_end_time:
                reverse = False

        # 绘制美化界面
        screen.fill(BG_COLOR)
        draw_cartoon_bg(screen)
        if game_state == "start":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            draw_text_with_bg(screen, "贪吃蛇游戏", big_font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80), WHITE, (0, 0, 0), 16, 200)
            draw_text_with_bg(screen, "按空格键开始游戏", font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), WHITE, (0, 0, 0), 12, 180)
        elif game_state == "playing":
            snake.draw(screen)
            food.draw(screen)
            obstacle.draw(screen)
            draw_text_with_bg(screen, f"分数: {snake.score}", font, (70, 30), WHITE, (0, 0, 0), 8, 160)
            draw_text_with_bg(screen, f"关卡: {level}", font, (200, 30), WHITE, (0, 0, 0), 8, 160)
            if invincible:
                draw_text_with_bg(screen, "无敌中", font, (350, 30), (0,255,120), (0,0,0), 8, 160)
            if reverse:
                draw_text_with_bg(screen, "反向中", font, (470, 30), (255,120,0), (0,0,0), 8, 160)
            draw_text_with_bg(screen, f"连击: {combo}", font, (600, 30), (255,200,0), (0,0,0), 8, 160)
            draw_text_with_bg(screen, f"限时: {max(0, int(12-(time.time()-last_eat_time)))}", font, (730, 30), (0,200,255), (0,0,0), 8, 160)
        elif game_state == "game_over":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            draw_text_with_bg(screen, "游戏结束", big_font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80), RED, (0, 0, 0), 16, 220)
            draw_text_with_bg(screen, f"最终分数: {snake.score}", font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), WHITE, (0, 0, 0), 12, 180)
            draw_text_with_bg(screen, "按R键重玩，ESC退出", font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60), WHITE, (0, 0, 0), 12, 180)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()    