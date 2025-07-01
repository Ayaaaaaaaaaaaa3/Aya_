import pygame

class Snake:
    def __init__(self):
        # 初始化蛇
        self.body = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.grow = False
        self.speed = 1 # 初始速度

    def move(self):
        # 移动蛇
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
        # 吃食物后增长
        self.grow = True

    def check_collision(self, width, height, obstacles):
        # 检查碰撞
        head = self.body[0]
        # 撞墙
        if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
            return True
        # 撞自己
        if head in self.body[1:]:
            return True
        # 撞障碍物
        if head in obstacles:
            return True
        return False
