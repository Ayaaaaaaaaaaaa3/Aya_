import random

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.obstacles = []
        self.sand_areas = []
        self.thorns = []
        self.blackholes = []
        self.moving_obstacles = []  # 移动障碍物（和尚）
        self.water_areas = []       # 水区
        self.rescue_points = []     # 救援点
        self.fog_areas = []         # 迷雾区
        self.thunder_zones = []     # 雷电区

    def generate_obstacles(self, level):
        self.obstacles = []
        for _ in range(level * 3):
            self.obstacles.append((random.randint(0, self.width-1), random.randint(0, self.height-1)))

    def set_obstacles(self, obstacle_type):
        self.obstacles = []
        self.moving_obstacles = []
        self.water_areas = []
        self.rescue_points = []
        self.fog_areas = []
        self.thunder_zones = []
        if obstacle_type == "bridge":
            # 生成桥墩障碍
            for x in range(self.width//3, self.width//3*2):
                self.obstacles.append((x, self.height//2))
        elif obstacle_type == "monk":
            # 巡逻和尚初始位置
            self.moving_obstacles = [(self.width//2, y) for y in range(5, 10)]
        elif obstacle_type == "narrow":
            # 地图变窄，左右加障碍
            for y in range(self.height):
                self.obstacles.append((0, y))
                self.obstacles.append((self.width-1, y))
        elif obstacle_type == "water":
            # 初始水区
            for x in range(self.width//4, self.width//4*3):
                self.water_areas.append((x, self.height//3))
        elif obstacle_type == "rescue":
            # 救援点
            self.rescue_points = [(self.width//2, self.height//2)]
        elif obstacle_type == "fog":
            # 迷雾区
            for x in range(self.width//3, self.width//3*2):
                for y in range(self.height//3, self.height//3*2):
                    self.fog_areas.append((x, y))
        elif obstacle_type == "thunder":
            # 雷电区初始为空，后续动态生成
            self.thunder_zones = []
        elif obstacle_type == "boss":
            # boss关障碍可自定义
            pass
        # 其它类型可扩展

    def generate_sand(self):
        self.sand_areas = []
        for _ in range(2):
            self.sand_areas.append((random.randint(0, self.width-1), random.randint(0, self.height-1)))

    def generate_thorns(self):
        self.thorns = []
        for _ in range(2):
            self.thorns.append((random.randint(0, self.width-1), random.randint(0, self.height-1)))

    def generate_blackholes(self):
        self.blackholes = []
        for _ in range(1):
            self.blackholes.append((random.randint(0, self.width-1), random.randint(0, self.height-1)))

    def update_moving_obstacles(self):
        # 简单上下巡逻和尚
        if not self.moving_obstacles:
            return
        new_positions = []
        for x, y in self.moving_obstacles:
            if y < self.height - 1:
                new_positions.append((x, y+1))
            else:
                new_positions.append((x, 5))
        self.moving_obstacles = new_positions

    def update_water_areas(self):
        # 水区周期性移动
        if not self.water_areas:
            return
        new_areas = []
        for x, y in self.water_areas:
            new_y = y + 1 if y + 1 < self.height else self.height//3
            new_areas.append((x, new_y))
        self.water_areas = new_areas

    def update_thunder_zones(self):
        # 随机生成雷电落点
        self.thunder_zones = []
        for _ in range(2):
            self.thunder_zones.append((random.randint(0, self.width-1), random.randint(0, self.height-1)))
