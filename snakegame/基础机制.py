import random

class BaseLevel:
    def __init__(self, game):
        self.game = game
        self.target_score = 10

    def setup(self):
        """初始化关卡元素"""
        self.game.snake.reset()
        self.game.score = 0
        self.game.target_score = self.target_score
        # 使用obstacles.py的障碍物系统，不需要重新设置

    def update(self):
        """每帧更新特殊机制"""
        pass

# 1. 西湖初遇
class Level1(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10  # 吃10个青蛇果
        # 无障碍物，使用obstacles.py的默认设置

# 2. 断桥相会
class Level2(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        # 桥墩障碍由obstacles.py的_generate_bridge_piers()生成

# 3. 金山寺门前
class Level3(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 12
        # 移动和尚由obstacles.py的_generate_monks()生成

# 4. 雷峰塔下
class Level4(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        self.game.snake.speed = 2  # 蛇速度加快
        # 窄路径由obstacles.py的_generate_narrow_path()生成

# 5. 水漫金山
class Level5(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        # 水区域由obstacles.py的_generate_water_zones()生成

# 6. 白蛇斗法
class Level6(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        # 魔法物品由obstacles.py的_generate_magic_items()生成

# 7. 小青救主
class Level7(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10
        # 救援点由obstacles.py的_generate_rescue_points()生成

# 8. 迷雾幻境
class Level8(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 16
        # 迷雾区域由obstacles.py的_generate_fog_zones()生成

# 9. 天降雷罚
class Level9(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        # 雷电区域和雷电攻击由obstacles.py的_generate_lightning_zones()和_generate_lightning_strikes()生成

# 10. 终极BOSS 法海
class Level10(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        # 法海BOSS由obstacles.py的_generate_fahai_boss()生成
        # 护身符由obstacles.py的_generate_amulets()生成

# 关卡选择器
def get_level(level_num, game):
    levels = [Level1, Level2, Level3, Level4, Level5, Level6, Level7, Level8, Level9, Level10]
    return levels[level_num-1](game)