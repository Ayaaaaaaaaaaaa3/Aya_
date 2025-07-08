import pygame
import random
import math
import os

class Boss:
    MOVE_INTERVAL = 20  # 移动间隔帧数
    BALL_COOLDOWN = 30  # 法球冷却帧数

    def __init__(self, x, y, size, image_path=None, **kwargs):
        self.x, self.y, self.size = x, y, size
        self.boss_scale = 5.0  # BOSS图片放大5倍
        self.image = self._load_boss_image(image_path)
        self.ball_image = self._load_ball_image()  # 加载法球图片
        self.alive = True
        self.move_counter = 0
        self.mode = "normal"  # normal, final
        self.balls = []  # 法球列表
        self.ball_cooldown = 0
        self.weak = False  # 虚弱状态
        self.circle_count = 0  # 蛇绕圈计数
        self.last_snake_angle = None

    def _load_boss_image(self, image_path):
        # 优先用传入路径，否则用默认boss图片
        target_size = int(self.size * self.boss_scale)
        if image_path and os.path.exists(image_path):
            print(f"加载自定义boss图片: {image_path}")
            return pygame.transform.scale(pygame.image.load(image_path), (target_size, target_size))
        default_path = "assets/obstacles/boss4.png"
        if os.path.exists(default_path):
            print(f"加载默认boss图片: {default_path}")
            return pygame.transform.scale(pygame.image.load(default_path), (target_size, target_size))
        print("未找到boss图片")
        return None

    def _load_ball_image(self):
        # 加载法球图片
        ball_path = "assets/obstacles/ball.png"
        if os.path.exists(ball_path):
            print(f"加载法球图片: {ball_path}")
            return pygame.transform.scale(pygame.image.load(ball_path), (self.size * 3, self.size * 3))  # 从1倍改为3倍
        print("未找到法球图片，使用默认圆形")
        return None

    def set_mode(self, mode):
        self.mode = mode

    def move(self, width, height, obstacles, target_pos=None):
        self.move_counter += 1
        if self.move_counter < self.MOVE_INTERVAL:
            return
        self.move_counter = 0
        for dx, dy in random.sample([(1,0), (-1,0), (0,1), (0,-1)], 4):
            nx, ny = self.x + dx, self.y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in obstacles:
                self.x, self.y = nx, ny
                break
        if self.mode == "final" and not self.weak:
            self.shoot_ball(target_pos)
            self.move_balls()

    def shoot_ball(self, target_pos=None):
        if self.ball_cooldown > 0:
            self.ball_cooldown -= 1
            return
        self.ball_cooldown = self.BALL_COOLDOWN
        if not target_pos:
            return
        bx, by = self.x, self.y
        tx, ty = target_pos
        dx, dy = tx - bx, ty - by
        dist = math.hypot(dx, dy) or 1
        dir_vec = (dx / dist, dy / dist)
        self.balls.append({"pos": [bx, by], "dir": dir_vec})

    def move_balls(self):
        new_balls = []
        for ball in self.balls:
            ball["pos"][0] += ball["dir"][0]
            ball["pos"][1] += ball["dir"][1]
            if 0 <= ball["pos"][0] < self.size and 0 <= ball["pos"][1] < self.size:
                new_balls.append(ball)
        self.balls = new_balls

    def check_ball_hit(self, snake_body):
        for ball in self.balls:
            bx, by = ball["pos"]
            for seg in snake_body:
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
                diff -= math.copysign(2 * math.pi, diff)
            if diff > 2.5:
                self.circle_count += 1
        self.last_snake_angle = angle

    def draw(self, surface):
        if self.image:
            surface.blit(self.image, (self.x * self.size, self.y * self.size))
        else:
            # 图片未加载时，画一个红色十字作为定位标志
            center_x = self.x * self.size + self.size // 2
            center_y = self.y * self.size + self.size // 2
            length = self.size // 2
            pygame.draw.line(surface, (255, 0, 0), (center_x - length, center_y), (center_x + length, center_y), 2)
            pygame.draw.line(surface, (255, 0, 0), (center_x, center_y - length), (center_x, center_y + length), 2)
        # 绘制法球
        for ball in self.balls:
            bx, by = ball["pos"]
            if self.ball_image:
                surface.blit(self.ball_image, (int(bx * self.size + self.size // 2 - self.ball_image.get_width() // 2),
                                              int(by * self.size + self.size // 2 - self.ball_image.get_height() // 2)))
            else:
                pygame.draw.circle(surface, (0, 0, 255), (int(bx * self.size + self.size // 2), int(by * self.size + self.size // 2)), self.size)  # 从1/3改为1倍
