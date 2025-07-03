import random

class BaseLevel:
    def __init__(self, game):
        self.game = game
        self.target_score = 10
        self.obstacles = []
        self.specials = []

    def setup(self):
        """初始化关卡元素"""
        self.game.snake.reset()
        self.game.score = 0
        self.game.obstacles = self.obstacles
        self.game.specials = self.specials
        self.game.target_score = self.target_score

    def update(self):
        """每帧更新特殊机制"""
        pass

# 1. 西湖初遇
class Level1(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10  # 吃10个青蛇果
        self.obstacles = []     # 无障碍物

# 2. 断桥相会
class Level2(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        # 桥墩障碍
        self.obstacles = [(8, 8), (8, 9), (8, 10), (12, 8), (12, 9), (12, 10)]

# 3. 金山寺门前
class Level3(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 12
        self.monks = [{'pos': [5, 5], 'dir': 1}]  # 移动和尚
    def update(self):
        # 移动和尚障碍
        for monk in self.monks:
            monk['pos'][0] += monk['dir']
            if monk['pos'][0] > 15 or monk['pos'][0] < 5:
                monk['dir'] *= -1
        self.game.moving_obstacles = [tuple(m['pos']) for m in self.monks]

# 4. 雷峰塔下
class Level4(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        self.game.snake.speed = 2  # 蛇速度加快
        self.game.map_size = (20, 10)  # 地图变窄

# 5. 水漫金山
class Level5(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        self.flood_zones = [(x, 5) for x in range(5, 15)]
        self.flood_timer = 0
        self.flood_on = False
    def update(self):
        # 周期性水淹
        self.flood_timer += 1
        if self.flood_timer % 100 == 0:
            self.flood_on = not self.flood_on
        if self.flood_on:
            self.game.flood_zones = self.flood_zones
        else:
            self.game.flood_zones = []

# 6. 白蛇斗法
class Level6(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        self.magic_items = [(random.randint(1, 18), random.randint(1, 18))]
    def update(self):
        # 吃到法宝短暂无敌
        if self.game.snake.head in self.magic_items:
            self.game.snake.invincible = 50  # 50帧无敌
            self.magic_items.remove(self.game.snake.head)

# 7. 小青救主
class Level7(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10
        self.rescue_points = [(3, 3), (16, 16)]
        self.visited = set()
    def update(self):
        # 到达救援点奖励分数
        if self.game.snake.head in self.rescue_points and self.game.snake.head not in self.visited:
            self.game.score += 2
            self.visited.add(self.game.snake.head)

# 8. 迷雾幻境
class Level8(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 16
        self.fog_areas = [(x, y) for x in range(5, 15) for y in range(5, 15)]
    def update(self):
        # 进入迷雾区视野受限（可在渲染时处理）
        self.game.fog_areas = self.fog_areas

# 9. 天降雷罚
class Level9(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        self.thunder_pos = None
        self.thunder_timer = 0
    def update(self):
        # 随机雷电
        self.thunder_timer += 1
        if self.thunder_timer % 60 == 0:
            self.thunder_pos = (random.randint(1, 18), random.randint(1, 18))
        if self.game.snake.head == self.thunder_pos:
            self.game.snake.alive = False

# 10. 终极BOSS 法海
class Level10(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        self.boss = {'pos': [10, 10], 'hp': 3}
        self.boss_attack_timer = 0
        self.boss_balls = []
        self.rounds = 0
    def update(self):
        # 法海发射法球
        self.boss_attack_timer += 1
        if self.boss_attack_timer % 30 == 0:
            # 发射法球
            self.boss_balls.append([self.boss['pos'][0], self.boss['pos'][1], random.choice([(1,0),(-1,0),(0,1),(0,-1)])])
        # 法球移动
        for ball in self.boss_balls:
            ball[0] += ball[2][0]
            ball[1] += ball[2][1]
        # 检查碰撞
        for ball in self.boss_balls:
            if (ball[0], ball[1]) == self.game.snake.head:
                if not self.game.snake.invincible:
                    self.game.snake.alive = False
        # 吃满佛珠果后，绕BOSS三圈
        if self.game.score >= self.target_score:
            if self.game.snake.head == tuple(self.boss['pos']):
                self.rounds += 1
            if self.rounds >= 3:
                self.game.win = True

# 关卡选择器
def get_level(level_num, game):
    levels = [Level1, Level2, Level3, Level4, Level5, Level6, Level7, Level8, Level9, Level10]
    return levels[level_num-1](game)