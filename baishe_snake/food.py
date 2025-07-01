import random

class Food:
    def __init__(self, width, height, snake_body, obstacles, fruit_name="食物"):
        self.width = width
        self.height = height
        self.snake_body = snake_body
        self.obstacles = obstacles
        self.position = self.random_position()
        self.type = "normal"  # normal, special, positive, negative
        self.fruit_name = fruit_name

    def random_position(self):
        while True:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos not in self.snake_body and pos not in self.obstacles:
                return pos

    def respawn(self, snake_body, obstacles):
        self.snake_body = snake_body
        self.obstacles = obstacles
        self.position = self.random_position()
        # 随机类型
        r = random.random()
        if r < 0.7:
            self.type = "normal"
        elif r < 0.85:
            self.type = "special"
        elif r < 0.93:
            self.type = "positive"
        else:
            self.type = "negative"

    def set_type(self, fruit_name):
        self.fruit_name = fruit_name
