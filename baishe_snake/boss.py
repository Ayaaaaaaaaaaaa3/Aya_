import pygame
import random
import math

class Boss:
    def __init__(self, x, y, size, image_path=None, **kwargs):
        self.x = x
        self.y = y
        self.size = size
        self.image_path = image_path
        self.image = None
        if image_path:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (size, size))
        self.alive = True
        self.move_counter = 0  # 控制移动频率
        self.mode = "normal"  # normal, final
        # 第十关相关
        self.balls = []  # 法球列表，每个元素为dict: {"pos": [x, y], "dir": (dx, dy)}
        self.ball_cooldown = 0
        self.weak = False  # 虚弱状态
        self.circle_count = 0  # 蛇绕圈计数
        self.last_snake_angle = None

    def set_mode(self, mode):
        self.mode = mode

    def move(self, width, height, obstacles, target_pos=None):
        self.move_counter += 1
        if self.move_counter < 20:
            return
        self.move_counter = 0
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            new_pos = (self.x+dx, self.y+dy)
            if 0 <= new_pos[0] < width and 0 <= new_pos[1] < height and new_pos not in obstacles:
                self.x = new_pos[0]
                self.y = new_pos[1]
                break
        # 终极boss特殊行为
        if self.mode == "final" and not self.weak:
            self.shoot_ball(target_pos)
            self.move_balls()

    def shoot_ball(self, target_pos=None):
        # 每30帧发射一次法球，朝向蛇头
        if self.ball_cooldown > 0:
            self.ball_cooldown -= 1
            return
        self.ball_cooldown = 30
        if target_pos is None:
            return
        bx, by = self.x, self.y
        tx, ty = target_pos
        dx = tx - bx
        dy = ty - by
        dist = math.hypot(dx, dy)
        if dist == 0:
            dir_vec = (1, 0)
        else:
            dir_vec = (dx / dist, dy / dist)
        self.balls.append({"pos": [bx + 0.0, by + 0.0], "dir": dir_vec})

    def move_balls(self):
        # 法球移动，超出地图移除
        new_balls = []
        for ball in self.balls:
            ball["pos"][0] += ball["dir"][0]
            ball["pos"][1] += ball["dir"][1]
            # 只要法球中心还在地图内就保留
            if 0 <= ball["pos"][0] < self.size and 0 <= ball["pos"][1] < self.size:
                new_balls.append(ball)
        self.balls = new_balls

    def check_ball_hit(self, snake_body):
        # 检查法球是否击中蛇
        for ball in self.balls:
            bx, by = ball["pos"]
            for seg in snake_body:
                # 允许法球中心与蛇身格子重叠即判定击中
                if int(round(bx)) == seg[0] and int(round(by)) == seg[1]:
                    return True
        return False

    def clear_balls(self):
        self.balls = []

    def set_weak(self, weak=True):
        self.weak = weak
        if weak:
            self.clear_balls()

    def update_circle(self, snake_head):
        bx, by = self.x, self.y
        sx, sy = snake_head
        angle = math.atan2(sy - by, sx - bx)
        if self.last_snake_angle is not None:
            diff = angle - self.last_snake_angle
            if abs(diff) > math.pi:
                diff -= math.copysign(2*math.pi, diff)
            if diff > 2.5:
                self.circle_count += 1
        self.last_snake_angle = angle

    def draw(self, surface):
        if self.image:
            # 把格子坐标转为像素坐标
            surface.blit(self.image, (self.x * self.size, self.y * self.size))
        else:
            pygame.draw.rect(surface, (255, 0, 0), (self.x * self.size, self.y * self.size, self.size, self.size))
            boss_center = (self.x * self.size + self.size//2, self.y * self.size + self.size//2)
            pygame.draw.circle(surface, (220, 220, 220), boss_center, self.size//2+8)
            pygame.draw.arc(surface, (255, 215, 0), (boss_center[0]-self.size//2, boss_center[1]-self.size//2-10, self.size, self.size//2), 3.14, 0, 4)
            pygame.draw.circle(surface, (0,0,0), (boss_center[0]-self.size//6, boss_center[1]-self.size//8), self.size//8)
            pygame.draw.circle(surface, (0,0,0), (boss_center[0]+self.size//6, boss_center[1]-self.size//8), self.size//8)
            pygame.draw.arc(surface, (128,128,128), (boss_center[0]-self.size//3, boss_center[1]+self.size//6, self.size//3, self.size//4), 3.14, 0, 2)
            pygame.draw.arc(surface, (128,128,128), (boss_center[0], boss_center[1]+self.size//6, self.size//3, self.size//4), 3.14, 0, 2)
            for ball in self.balls:
                bx, by = ball["pos"]
                pygame.draw.circle(surface, (0, 0, 255), (int(bx*self.size + self.size//2), int(by*self.size + self.size//2)), self.size//3)
