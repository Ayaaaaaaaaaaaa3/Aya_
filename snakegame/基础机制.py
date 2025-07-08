import random

class BaseLevel:
    def __init__(self, game):
        self.game = game
        self.target_score = 10
        self.background_image = None  # 默认无背景

    def setup(self):
        """初始化关卡元素"""
        self.game.snake.reset()
        self.game.score = 0
        self.game.target_score = self.target_score
        # 使用obstacles.py的障碍物系统，不需要重新设置

    def update(self):
        """每帧更新特殊机制"""
        pass

    def get_background_image(self):
        """获取关卡背景图片路径"""
        return self.background_image

# 1. 西湖初遇
class Level1(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10  # 吃10个青蛇果
        self.background_image = "assets/level1_bg.jpg"  # 关卡1背景图片
        # 无障碍物，使用obstacles.py的默认设置

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        # 可以在这里添加关卡1特有的设置
        print("进入关卡1：西湖初遇")

# 2. 断桥相会
class Level2(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        self.background_image = "assets/level2_bg.jpg"  # 关卡2背景图片
        # 桥墩障碍由obstacles.py的_generate_bridge_piers()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡2：断桥相会")

# 3. 金山寺门前
class Level3(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 12
        self.background_image = "assets/level3_bg.jpg"  # 关卡3背景图片
        # 移动和尚由obstacles.py的_generate_monks()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡3：金山寺门前")

# 4. 雷峰塔下
class Level4(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        self.background_image = "assets/level4_bg.jpg"  # 关卡4背景图片
        self.game.snake.speed = 2  # 蛇速度加快
        # 窄路径由obstacles.py的_generate_narrow_path()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡4：雷峰塔下")

# 5. 水漫金山
class Level5(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        self.background_image = "assets/level5_bg.jpg"  # 关卡5背景图片
        # 水区域由obstacles.py的_generate_water_zones()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡5：水漫金山")

# 6. 白蛇斗法
class Level6(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 15
        self.background_image = "assets/level6_bg.jpg"  # 关卡6背景图片
        # 魔法物品由obstacles.py的_generate_magic_items()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡6：白蛇斗法")

# 7. 小青救主
class Level7(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 10
        self.background_image = "assets/level7_bg.jpg"  # 关卡7背景图片
        # 救援点由obstacles.py的_generate_rescue_points()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡7：小青救主")

# 8. 迷雾幻境
class Level8(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 16
        self.background_image = "assets/level8_bg.jpg"  # 关卡8背景图片
        # 迷雾区域由obstacles.py的_generate_fog_zones()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡8：迷雾幻境")

# 9. 天降雷罚
class Level9(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 18
        self.background_image = "assets/level9_bg.jpg"  # 关卡9背景图片
        # 雷电区域和雷电攻击由obstacles.py的_generate_lightning_zones()和_generate_lightning_strikes()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡9：天降雷罚")

# 10. 终极BOSS 法海
class Level10(BaseLevel):
    def __init__(self, game):
        super().__init__(game)
        self.target_score = 20
        self.background_image = "assets/level10_bg.jpg"  # 关卡10背景图片
        # 法海BOSS由obstacles.py的_generate_fahai_boss()生成
        # 护身符由obstacles.py的_generate_amulets()生成

    def setup(self):
        """初始化关卡元素"""
        super().setup()
        print("进入关卡10：终极BOSS法海")

# 关卡选择器
def get_level(level_num, game):
    levels = [Level1, Level2, Level3, Level4, Level5, Level6, Level7, Level8, Level9, Level10]
    return levels[level_num-1](game)