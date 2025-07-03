"""
food属性介绍：
Food系统负责管理游戏中各种类型的食物，
包括10种不同关卡对应的特色食物（如青蛇果、莲花果、灵芝果等），
每种食物都有独特的视觉效果和特殊效果，如加速、反向控制、无敌状态等。
食物会随机生成在场景中，
当蛇头与食物碰撞时会触发相应效果，
并累计食物计数以达成关卡目标。

食物分为普通和特殊，吃到特殊食物得分翻倍
每一关卡根据主题设计了不同样式的食物
部分关卡还有技能食物，提供一些效果
完成目标即可进入下一关
"""
import random
import pygame
import os
from config import *
from collections import deque

class GameEntity:
    def __init__(self, current_level=1):
        # 蛇的属性
        # 初始化蛇的位置（3节，水平向右）
        self.positions = []
        start_x, start_y = GRID_WIDTH//2, GRID_HEIGHT//2
        for i in range(START_LENGTH):
            self.positions.append((start_x - i, start_y))  # 水平向右排列3节
        
        self.direction = RIGHT
        self.next_direction = RIGHT
        self.length = START_LENGTH
        self.score = 0
        self.speed = INITIAL_SPEED
        self.reverse_controls = False
        self.special_effects = {}
        self.growth_pending = 0
        self.color_head = YELLOW
        self.color_body = GREEN
        
        # 食物属性
        self.food_position = (0, 0)
        self.food_type = "normal"
        self.images = self._load_images()
        self.current_food_image = self.images[self.food_type]
        self.radius = GRID_SIZE // 3
        self.current_level = current_level
        self.food_count = 0  # 当前关卡已吃食物计数
        self.level_targets = {
            1: {"target": 10, "food_type": "green_fruit"},
            2: {"target": 15, "food_type": "lotus_fruit"},
            3: {"target": 12, "food_type": "ganoderma"},
            4: {"target": 18, "food_type": "herb"},
            5: {"target": 20, "food_type": "water_fruit"},
            6: {"target": 15, "food_type": "magic_fruit"},
            7: {"target": 10, "food_type": "vine_fruit"},
            8: {"target": 16, "food_type": "illusion_fruit"},
            9: {"target": 18, "food_type": "lightning_fruit"},
            10: {"target": 20, "food_type": "bead_fruit"}
        }
        self.randomize_food_position()
    
    # ===== 蛇相关方法 =====
    def get_head_position(self):
        return self.positions[0]
    
    def update_snake(self):
        """更新蛇的位置和状态（修复版）"""
        # 应用当前方向（考虑反向控制）
        if not self.reverse_controls:
            self.direction = self.next_direction
        else:
            # 反向控制：实际移动方向与输入相反
            self.direction = (-self.next_direction[0], -self.next_direction[1])
        
        head = self.get_head_position()
        x, y = self.direction
        
        new_x = (head[0] + x) % GRID_WIDTH
        new_y = (head[1] + y) % GRID_HEIGHT
        new_pos = (new_x, new_y)
        
        # 检查是否撞到自己（排除尾部节点）
        if new_pos in self.positions[:-1]:
            return False
            
        self.positions.insert(0, new_pos)
        
        # 处理增长
        if self.growth_pending > 0:
            self.growth_pending -= 1
        else:
            if len(self.positions) > self.length:
                self.positions.pop()
        
        # 更新特殊效果持续时间
        for effect in list(self.special_effects.keys()):
            self.special_effects[effect] -= 1
            if self.special_effects[effect] <= 0:
                del self.special_effects[effect]
                if effect == "reverse":
                    self.reverse_controls = False
                elif effect == "speed_up":
                    self.speed = INITIAL_SPEED
                elif effect == "speed_down":
                    self.speed = INITIAL_SPEED
        
        return True

    def change_direction(self, direction):
        """改变蛇的方向（带缓冲防止180度转弯）"""
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.next_direction = direction
    
    def grow(self, amount=1):
        self.growth_pending += amount
    
    def shrink(self, amount=1):
        self.length = max(1, self.length - amount)
        while len(self.positions) > self.length:
            self.positions.pop()
    
    def change_speed(self, factor):
        self.speed = max(MIN_SPEED, min(MAX_SPEED, self.speed * factor))
        if factor > 1:  # 加速
            self.special_effects["speed_up"] = FOOD_TYPES["speed_up"]["duration"]
        elif factor < 1:  # 减速
            self.special_effects["speed_down"] = FOOD_TYPES["speed_down"]["duration"]
    
    def reverse_direction(self):
        self.reverse_controls = True
        self.special_effects["reverse"] = FOOD_TYPES["reverse"]["duration"]
    
    def render_snake(self, surface):
        for i, p in enumerate(self.positions):
            color = self.color_head if i == 0 else self.color_body
            if "reverse" in self.special_effects and i % 2 == 0:
                color = (255 - color[0], 255 - color[1], 255 - color[2])
            
            rect = pygame.Rect(
                p[0] * GRID_SIZE, p[1] * GRID_SIZE,
                GRID_SIZE, GRID_SIZE
            )
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)
            
            if i == 0 and self.special_effects:
                center = (p[0] * GRID_SIZE + GRID_SIZE//2, p[1] * GRID_SIZE + GRID_SIZE//2)
                pygame.draw.circle(surface, (255, 255, 255, 128), center, GRID_SIZE//4)
    
    # ===== 食物相关方法 =====
    def _load_images(self):
        """加载所有食物图片资源"""
        images = {}
        try:
            if not os.path.exists("assets/food"):
                os.makedirs("assets/food")
            
            # 更新食物类型以匹配关卡设计
            level_food_types = {
                "green_fruit": (0, 255, 0),    # 青蛇果 - 绿色
                "lotus_fruit": (255, 192, 203), # 莲花果 - 粉色
                "ganoderma": (210, 180, 140),   # 灵芝果 - 棕色
                "herb": (50, 205, 50),          # 仙草果 - 浅绿色
                "water_fruit": (64, 224, 208),  # 水灵果 - 浅蓝色
                "magic_fruit": (138, 43, 226),  # 法力果 - 紫色
                "vine_fruit": (34, 139, 34),    # 青藤果 - 深绿色
                "illusion_fruit": (147, 112, 219), # 幻境果 - 中紫色
                "lightning_fruit": (255, 255, 0), # 雷电果 - 黄色
                "bead_fruit": (255, 215, 0)     # 佛珠果 - 金色
            }
            
            for food_type, color in level_food_types.items():
                img_path = f"assets/food/{food_type}.png"
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    images[food_type] = pygame.transform.scale(img, (GRID_SIZE, GRID_SIZE))
                else:
                    surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                    pygame.draw.circle(surf, color + (255,), (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2-2)
                    images[food_type] = surf
        except Exception as e:
            print(f"图片加载失败: {str(e)}")
            # 创建默认食物图像
            level_food_types = {
                "green_fruit": (0, 255, 0),
                "lotus_fruit": (255, 192, 203),
                "ganoderma": (210, 180, 140),
                "herb": (50, 205, 50),
                "water_fruit": (64, 224, 208),
                "magic_fruit": (138, 43, 226),
                "vine_fruit": (34, 139, 34),
                "illusion_fruit": (147, 112, 219),
                "lightning_fruit": (255, 255, 0),
                "bead_fruit": (255, 215, 0)
            }
            for food_type, color in level_food_types.items():
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2-2)
                images[food_type] = surf
        return images
    
    def randomize_food_position(self):
        """安全地随机生成食物位置"""
        max_attempts = 100
        for _ in range(max_attempts):
            self.food_position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            if self.food_position not in self.positions:
                break
        
        # 根据当前关卡设置食物类型
        if self.current_level in self.level_targets:
            self.food_type = self.level_targets[self.current_level]["food_type"]
        else:
            self.food_type = "green_fruit"  # 默认
        
        self.current_food_image = self.images[self.food_type]
    
    def check_food_collision(self):
        """检测食物碰撞"""
        head = self.get_head_position()
        head_x = head[0] * GRID_SIZE + GRID_SIZE // 2
        head_y = head[1] * GRID_SIZE + GRID_SIZE // 2
        food_x = self.food_position[0] * GRID_SIZE + GRID_SIZE // 2
        food_y = self.food_position[1] * GRID_SIZE + GRID_SIZE // 2
        dx = food_x - head_x
        dy = food_y - head_y
        distance_squared = dx*dx + dy*dy
        return distance_squared <= (self.radius ** 2)
    
    def apply_food_effect(self):
        """应用食物效果"""
        # 增加食物计数
        self.food_count += 1
        
        # 根据关卡不同可能有不同效果
        if self.current_level == 6:  # 白蛇斗法关卡 - 法力果提供短暂无敌
            self.special_effects["invincible"] = 100  # 100帧无敌时间
            return 2
        elif self.current_level == 10:  # 最终BOSS关卡 - 佛珠果
            if self.food_count >= self.level_targets[10]["target"]:
                return 5  # 特殊返回值表示BOSS虚弱状态
            return 3
        else:
            self.grow()
            return 1
    
    def render_food(self, surface):
        """渲染食物"""
        img_rect = self.current_food_image.get_rect(
            center=(self.food_position[0] * GRID_SIZE + GRID_SIZE//2,
                   self.food_position[1] * GRID_SIZE + GRID_SIZE//2))
        surface.blit(self.current_food_image, img_rect)
    
    def is_level_complete(self):
        """检查是否完成当前关卡目标"""
        if self.current_level in self.level_targets:
            return self.food_count >= self.level_targets[self.current_level]["target"]
        return False
    
    def advance_level(self):
        """进入下一关"""
        if self.current_level < 10:
            self.current_level += 1
            self.food_count = 0
            self.randomize_food_position()
            return True
        return False