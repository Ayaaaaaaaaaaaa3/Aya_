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
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_head = (new_x, new_y)
        
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
        for p in self.positions:
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), 
                             (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, WHITE, rect, 1)

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
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE),
                         (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.color, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)

def draw_grid(surface):
    """绘制网格背景"""
    for y in range(0, GRID_HEIGHT):
        for x in range(0, GRID_WIDTH):
            rect = pygame.Rect((x * GRID_SIZE, y * GRID_SIZE),
                             (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

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
    
    # 游戏主循环
    running = True
    while running:
        # 控制游戏速度
        clock.tick(10)  # 游戏速度，数值越大越快
        
        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
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
        
        # 移动蛇
        if not snake.move():
            # 碰撞重置游戏
            food.randomize_position()
        
        # 检查是否吃到食物
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 1
            food.randomize_position()
        
        # 绘制游戏元素
        screen.fill(BLACK)
        draw_grid(screen)
        snake.draw(screen)
        food.draw(screen)
        
        # 显示分数
        score_text = font.render(f"分数: {snake.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        # 更新显示
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()    