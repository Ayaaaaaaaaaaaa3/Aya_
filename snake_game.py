import pygame
import random
import sys

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

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()
        
    def randomize_position(self):
        """随机生成食物位置"""
        self.position = (random.randint(0, GRID_WIDTH - 1), 
                        random.randint(0, GRID_HEIGHT - 1))
    
    def draw(self, surface):
        """在屏幕上绘制食物"""
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
        # 食物用圆形
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

    # 游戏状态: start, playing, game_over
    game_state = "start"
    running = True
    
    # 新增大号字体
    big_font = pygame.font.SysFont(['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC'], 48)
    
    while running:
        clock.tick(10)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "start":
                    if event.key == pygame.K_SPACE:
                        game_state = "playing"
                        snake.reset()
                        food.randomize_position()
                elif game_state == "playing":
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
                        food.randomize_position()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

        if game_state == "playing":
            move_result = snake.move()
            if move_result == 'hit_wall':
                game_state = "game_over"
            elif move_result is False:
                game_state = "game_over"
            # 检查是否吃到食物
            if snake.get_head_position() == food.position:
                snake.length += 1
                snake.score += 1
                food.randomize_position()

        # 绘制美化界面
        screen.fill(BG_COLOR)
        if game_state == "start":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            draw_text_with_bg(screen, "贪吃蛇游戏", big_font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80), WHITE, (0, 0, 0), 16, 200)
            draw_text_with_bg(screen, "按空格键开始游戏", font, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), WHITE, (0, 0, 0), 12, 180)
        elif game_state == "playing":
            snake.draw(screen)
            food.draw(screen)
            draw_text_with_bg(screen, f"分数: {snake.score}", font, (70, 30), WHITE, (0, 0, 0), 8, 160)
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