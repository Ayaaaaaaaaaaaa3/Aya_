import pygame
import random
import math

class Boss:
    def __init__(self, width, height, cell_size):
        # 初始化boss
        self.width = width
        self.height = height
        self.position = (width // 2, height // 2)
        self.cell_size = cell_size
        self.alive = True
        self.move_counter = 0  # 控制移动频率
        self.mode = "normal"  # normal, final
        # boss关相关
        self.balls = []  # 法球列表，每个元素为dict: {"pos": [x, y], "dir": (dx, dy)}
        self.ball_cooldown = 0
        self.weak = False  # 虚弱状态
        self.circle_count = 0  # 蛇绕圈计数
        self.last_snake_angle = None

    def set_mode(self, mode):
        # 设置boss模式
        self.mode = mode

    def move(self, width, height, obstacles, target_pos=None):
        # boss移动逻辑
        self.move_counter += 1
        if self.move_counter < 20:
            return
        self.move_counter = 0
        dirs = [(1,0), (-1,0), (0,1), (0,-1)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            new_pos = (self.position[0]+dx, self.position[1]+dy)
            if 0 <= new_pos[0] < width and 0 <= new_pos[1] < height and new_pos not in obstacles:
                self.position = new_pos
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
        bx, by = self.position
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
            if 0 <= ball["pos"][0] < self.width and 0 <= ball["pos"][1] < self.height:
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
        # 清除所有法球
        self.balls = []

    def set_weak(self, weak=True):
        # 设置虚弱状态
        self.weak = weak
        if weak:
            self.clear_balls()

    def update_circle(self, snake_head):
        # 更新蛇绕圈计数
        bx, by = self.position
        sx, sy = snake_head
        angle = math.atan2(sy - by, sx - bx)
        if self.last_snake_angle is not None:
            diff = angle - self.last_snake_angle
            if abs(diff) > math.pi:
                diff -= math.copysign(2*math.pi, diff)
            if diff > 2.5:
                self.circle_count += 1
        self.last_snake_angle = angle

    def render(self, screen):
        # 绘制boss
        boss_center = (self.position[0]*self.cell_size + self.cell_size//2, self.position[1]*self.cell_size + self.cell_size//2)
        pygame.draw.circle(screen, (220, 220, 220), boss_center, self.cell_size//2+8)
        pygame.draw.arc(screen, (255, 215, 0), (boss_center[0]-self.cell_size//2, boss_center[1]-self.cell_size//2-10, self.cell_size, self.cell_size//2), 3.14, 0, 4)
        pygame.draw.circle(screen, (0,0,0), (boss_center[0]-self.cell_size//6, boss_center[1]-self.cell_size//8), self.cell_size//8)
        pygame.draw.circle(screen, (0,0,0), (boss_center[0]+self.cell_size//6, boss_center[1]-self.cell_size//8), self.cell_size//8)
        pygame.draw.arc(screen, (128,128,128), (boss_center[0]-self.cell_size//3, boss_center[1]+self.cell_size//6, self.cell_size//3, self.cell_size//4), 3.14, 0, 2)
        pygame.draw.arc(screen, (128,128,128), (boss_center[0], boss_center[1]+self.cell_size//6, self.cell_size//3, self.cell_size//4), 3.14, 0, 2)
        for ball in self.balls:
            bx, by = ball["pos"]
            pygame.draw.circle(screen, (0, 0, 255), (int(bx*self.cell_size + self.cell_size//2), int(by*self.cell_size + self.cell_size//2)), self.cell_size//3)
