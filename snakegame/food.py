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

class FoodSystem:
    def __init__(self, current_level=1):
        # 食物属性
        self.food_position = (0, 0)
        self.food_type = "green_fruit"  # 默认食物类型
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
    
    def _load_images(self):
        """加载所有食物图片资源"""
        images = {}
        
        # 食物类型颜色定义
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
        
        try:
            if not os.path.exists("assets/food"):
                os.makedirs("assets/food")
            
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
            for food_type, color in level_food_types.items():
                surf = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(surf, color, (GRID_SIZE//2, GRID_SIZE//2), GRID_SIZE//2-2)
                images[food_type] = surf
        return images
    
    def randomize_food_position(self, snake_positions=None):
        """安全地随机生成食物位置"""
        max_attempts = 100
        for _ in range(max_attempts):
            self.food_position = (
                random.randint(0, GRID_WIDTH - 1),
                random.randint(0, GRID_HEIGHT - 1)
            )
            # 如果提供了蛇的位置，确保食物不在蛇身上
            if snake_positions is None or self.food_position not in snake_positions:
                break
        
        # 根据当前关卡设置食物类型
        if self.current_level in self.level_targets:
            self.food_type = self.level_targets[self.current_level]["food_type"]
        else:
            self.food_type = "green_fruit"  # 默认
        
        self.current_food_image = self.images[self.food_type]
    
    def check_food_collision(self, snake_head):
        """检测食物碰撞"""
        head_x = snake_head[0] * GRID_SIZE + GRID_SIZE // 2
        head_y = snake_head[1] * GRID_SIZE + GRID_SIZE // 2
        food_x = self.food_position[0] * GRID_SIZE + GRID_SIZE // 2
        food_y = self.food_position[1] * GRID_SIZE + GRID_SIZE // 2
        dx = food_x - head_x
        dy = food_y - head_y
        distance_squared = dx*dx + dy*dy
        return distance_squared <= (self.radius ** 2)
    
    def apply_food_effect(self, snake):
        """应用食物效果"""
        # 增加食物计数
        self.food_count += 1
        
        # 根据关卡不同可能有不同效果
        if self.current_level == 6:  # 白蛇斗法关卡 - 法力果提供短暂无敌
            snake.special_effects = getattr(snake, 'special_effects', {})
            snake.special_effects["invincible"] = 100  # 100帧无敌时间
            return 2
        elif self.current_level == 10:  # 最终BOSS关卡 - 佛珠果
            if self.food_count >= self.level_targets[10]["target"]:
                return 5  # 特殊返回值表示BOSS虚弱状态
            return 3
        else:
            snake.eat()  # 调用蛇的eat方法
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
    
    def get_target_score(self):
        """获取当前关卡目标分数"""
        if self.current_level in self.level_targets:
            return self.level_targets[self.current_level]["target"]
        return 10 