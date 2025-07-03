# 游戏配置文件
import pygame

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 窗口设置
UI_WIDTH = 800  # 统一UI界面宽度
UI_HEIGHT = 600  # 统一UI界面高度
WINDOW_WIDTH = UI_WIDTH  # 游戏窗口宽度
WINDOW_HEIGHT = UI_HEIGHT  # 游戏窗口高度

# 游戏网格设置
GRID_SIZE = 20  # 调整网格大小为20像素
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE  # 40格
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE  # 30格
START_LENGTH = 3

# 游戏速度设置
INITIAL_SPEED = 1
MIN_SPEED = 0.5
MAX_SPEED = 3.0

# 食物类型配置
FOOD_TYPES = {
    "speed_up": {"duration": 100, "factor": 1.5},
    "speed_down": {"duration": 100, "factor": 0.7},
    "reverse": {"duration": 150, "factor": 1.0}
}

# 游戏速度
FPS = 5

# 关卡设置
MAX_LEVEL = 10

# 资源路径
ASSETS_PATH = "assets"
FOOD_PATH = f"{ASSETS_PATH}/food"
OBSTACLES_PATH = f"{ASSETS_PATH}/obstacles" 