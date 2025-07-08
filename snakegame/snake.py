import pygame

class Snake:
    def __init__(self):
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.grow = False
        self.speed = 1.0 # 初始速度，允许float
        self.special_effects = {}  # 特殊效果字典
        self.slow_timer = 0  # 水域减速计时器

    def move(self):
        # 按speed控制移动距离（主循环需支持小于1的速度）
        head = (self.body[0][0] + self.direction[0], self.body[0][1] + self.direction[1])
        self.body.insert(0, head)
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def change_direction(self, new_dir):
        # 防止反向
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir

    def eat(self):
        self.grow = True

    def check_collision(self, grid_width, grid_height, obstacle_positions, obstacle_types=None):
        head = self.body[0]
        # 撞墙
        if not (0 <= head[0] < grid_width and 0 <= head[1] < grid_height):
            return True
        # 撞自己
        if head in self.body[1:]:
            return True
        # 撞障碍物
        if obstacle_types is None:
            if head in obstacle_positions:
                return True
        else:
            for pos, typ in zip(obstacle_positions, obstacle_types):
                # 桥墩图片判定范围更大
                if typ == 'bridge_pier':
                    if abs(head[0] - pos[0]) < 1 and abs(head[1] - pos[1]) < 1:
                        return True
                # 其它障碍物精确判定
                elif head == pos:
                    return True
        return False

    def render(self, surface, cell_size):
        # 画蛇头
        head_x, head_y = self.body[0]
        center = (head_x * cell_size + cell_size // 2, head_y * cell_size + cell_size // 2)
        pygame.draw.circle(surface, (255, 255, 255), center, cell_size // 2)
        eye_radius = cell_size // 7
        eye_offset_x = cell_size // 5
        eye_offset_y = cell_size // 5
        dx, dy = self.direction
        if dx == 1:
            eye1 = (center[0] + eye_offset_x, center[1] - eye_offset_y)
            eye2 = (center[0] + eye_offset_x, center[1] + eye_offset_y)
        elif dx == -1:
            eye1 = (center[0] - eye_offset_x, center[1] - eye_offset_y)
            eye2 = (center[0] - eye_offset_x, center[1] + eye_offset_y)
        elif dy == 1:
            eye1 = (center[0] - eye_offset_x, center[1] + eye_offset_y)
            eye2 = (center[0] + eye_offset_x, center[1] + eye_offset_y)
        else:
            eye1 = (center[0] - eye_offset_x, center[1] - eye_offset_y)
            eye2 = (center[0] + eye_offset_x, center[1] - eye_offset_y)
        pygame.draw.circle(surface, (0, 0, 0), eye1, eye_radius)
        pygame.draw.circle(surface, (0, 0, 0), eye2, eye_radius)
        # 画蛇身
        for x, y in self.body[1:]:
            center = (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2)
            pygame.draw.circle(surface, (255, 255, 255), center, cell_size // 2)

    def reset(self):
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.grow = False
        self.speed = 1.0
        self.slow_timer = 0
