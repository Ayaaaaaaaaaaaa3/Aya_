"""
obstacles属性介绍：
Obstacles系统构建了游戏的挑战性元素，
包含静态障碍物、动态障碍物、危险区域和特殊物品四大类。
系统根据当前关卡（共10关）智能生成不同的障碍组合，
如桥墩、巡逻和尚、水淹区域、迷雾、雷电等，
每个关卡都有独特的障碍配置。动态障碍物会按照设定路径移动，
危险区域会产生减速、伤害等负面效果。
"""
import random
import pygame
import os
from config import GRID_SIZE, GRID_WIDTH, GRID_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT

class Obstacle:
    def __init__(self, current_level=1):
        self.current_level = current_level
        self.positions = []
        self.moving_obstacles = []
        self.hazard_zones = []
        self.special_items = []
        self.static_images = self._load_scalable_images("assets/obstacles/static")
        self.moving_images = self._load_moving_obstacle_images()
        self.hazard_images = self._load_hazard_images()
        self.special_item_images = self._load_special_item_images()
        self.generate_level_obstacles()
    
    def _load_scalable_images(self, folder_path):
        images = []
        try:
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            
            for img_file in os.listdir(folder_path):
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    img_path = os.path.join(folder_path, img_file)
                    img = pygame.image.load(img_path).convert_alpha()
                    images.append(img)
            
            if not images:
                default_img = self._create_default_image((139, 69, 19))
                images.append(default_img)
                
        except Exception as e:
            print(f"静态障碍物图片加载失败: {str(e)}")
            images.append(self._create_default_image((139, 69, 19)))
        
        return images
    
    def _load_moving_obstacle_images(self):
        images = {
            "monk": self._load_single_image("assets/obstacles/monk.png", (210, 180, 140), scale=2.0),
            "lightning": self._load_single_image("assets/obstacles/lightning.png", (255, 255, 0), scale=5.0)  # 闪电增大5倍
        }
        return images
    
    def _load_hazard_images(self):
        images = {
            "water": self._load_single_image("assets/obstacles/water.png", (64, 224, 208)),
            "fog": self._create_fog_image(),
            "lightning_zone": self._create_default_image((255, 255, 0, 100))
        }
        return images
    
    def _create_fog_image(self):
        """创建无边框的雾效果"""
        img = pygame.Surface((30, 30), pygame.SRCALPHA)  # GRID_SIZE
        pygame.draw.rect(img, (200, 200, 200, 200), (0, 0, 30, 30))  # 降低alpha值从128到80，更朦胧
        return img
    
    def _load_special_item_images(self):
        images = {
            "magic": self._load_single_image("assets/obstacles/magic.png", (138, 43, 226), scale=3.0),  # 法宝放大3倍
            "rescue": self._load_rescue_image("assets/obstacles/rescue.png", (0, 255, 0)),  # 救援点特殊处理
            "amulet": self._load_single_image("assets/obstacles/amulet.png", (255, 215, 0), scale=3.0)  # 护身符放大3倍
        }
        return images
    
    def _load_rescue_image(self, img_path, default_color):
        """特殊加载救援点图片，删除黑边框并增加透明度"""
        try:
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                # 创建新的surface用于处理透明度
                size = int(GRID_SIZE)
                new_img = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # 缩放原图
                scaled_img = pygame.transform.smoothscale(img, (size, size))
                
                # 获取像素数据并处理透明度
                pixel_array = pygame.PixelArray(scaled_img)
                for x in range(size):
                    for y in range(size):
                        color = scaled_img.get_at((x, y))
                        # 如果是黑色或接近黑色，设为透明
                        if color[0] < 50 and color[1] < 50 and color[2] < 50:
                            new_img.set_at((x, y), (0, 0, 0, 0))  # 完全透明
                        else:
                            # 增加透明度，降低alpha值
                            alpha = max(100, color[3] - 100)  # 降低透明度
                            new_img.set_at((x, y), (color[0], color[1], color[2], alpha))
                
                return new_img
            else:
                return self._create_rescue_default_image(default_color)
        except Exception as e:
            print(f"救援点图片加载失败: {img_path}, {str(e)}")
            return self._create_rescue_default_image(default_color)
    
    def _create_rescue_default_image(self, color):
        """创建救援点默认图片，无黑边框且半透明"""
        if len(color) == 3:
            color = color + (128,)  # 半透明
        img = pygame.Surface((30, 30), pygame.SRCALPHA)  # GRID_SIZE
        pygame.draw.rect(img, color, (0, 0, 30, 30))  # GRID_SIZE，无黑边框
        return img
    
    def _load_single_image(self, img_path, default_color, scale=1.0):
        try:
            if os.path.exists(img_path):
                img = pygame.image.load(img_path).convert_alpha()
                size = int(GRID_SIZE * scale)
                return pygame.transform.smoothscale(img, (size, size))
            else:
                return self._create_default_image(default_color)
        except Exception as e:
            print(f"图片加载失败: {img_path}, {str(e)}")
            return self._create_default_image(default_color)
    
    def _create_default_image(self, color):
        if len(color) == 3:
            color = color + (255,)
        img = pygame.Surface((30, 30), pygame.SRCALPHA)  # GRID_SIZE
        pygame.draw.rect(img, color, (0, 0, 30, 30))  # GRID_SIZE
        pygame.draw.rect(img, (0, 0, 0), (0, 0, 30, 30), 1)  # BLACK
        return img
    
    def generate_level_obstacles(self):
        self.positions = []
        self.moving_obstacles = []
        self.hazard_zones = []
        self.special_items = []
        
        if self.current_level == 1:
            pass
            
        elif self.current_level == 2:
            # 只生成一个桥墩，图片为格子的5倍大，真正居中于屏幕
            center_pos = (GRID_WIDTH // 2, GRID_HEIGHT // 2)
            img = self.static_images[0]
            big_size = int(GRID_SIZE * 15)
            img_big = pygame.transform.smoothscale(img, (big_size, big_size))
            self.positions.append({
                "position": center_pos,
                "image": img_big,
                "type": "bridge_pier",
                "center_pixel": True
            })
            
        elif self.current_level == 3:
            self._generate_monks(3)
            
        elif self.current_level == 4:
            self._generate_narrow_path()
            
        elif self.current_level == 5:
            self._generate_water_zones(3)
            
        elif self.current_level == 6:
            self._generate_magic_items(2)
            
        elif self.current_level == 7:
            self._generate_rescue_points(1)
            # 删除桥墩，只保留救援点
            
        elif self.current_level == 8:
            self._generate_fog_zones(1)
            
        elif self.current_level == 9:
            self._generate_lightning_strikes(4)  # 只保留移动的闪电攻击，删除闪电区域
            
        elif self.current_level == 10:
            self._generate_fahai_boss()
            self._generate_random_amulet()  # 随机生成一个护身符
    
    def _generate_bridge_piers(self, count=5):
        for _ in range(count):
            pos = self._get_valid_position()
            self.positions.append({
                "position": pos,
                "image": random.choice(self.static_images),
                "type": "bridge_pier"
            })
    
    def _generate_monks(self, count=3):
        for _ in range(count):
            pos = self._get_valid_position()
            self.moving_obstacles.append({
                "position": pos,
                "direction": random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)]),  # UP, DOWN, LEFT, RIGHT
                "image": self.moving_images["monk"],
                "timer": 0,
                "speed": 0.8,
                "type": "monk"
            })
    
    def _generate_narrow_path(self):
        wall_thickness = 8  # 墙厚度为8格
        wall_color = (255, 255, 255)  # 浅薄荷绿
        wall_img = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(wall_img, wall_color, (0, 0, GRID_SIZE, GRID_SIZE))
        for y in range(GRID_HEIGHT):
            if y % 8 != 0:
                # 左侧厚墙
                for x in range(wall_thickness):
                    self.positions.append({
                        "position": (x, y),
                        "image": wall_img,
                        "type": "wall"
                    })
                # 右侧厚墙
                for x in range(GRID_WIDTH - wall_thickness, GRID_WIDTH):
                    self.positions.append({
                        "position": (x, y),
                        "image": wall_img,
                        "type": "wall"
                    })
    
    def _generate_water_zones(self, count=3):
        for _ in range(count):
            pos = self._get_valid_position()
            self.hazard_zones.append({
                "position": pos,
                "radius": 180,  # 原45，扩大5倍
                "image": self.hazard_images["water"],
                "type": "water",
                "active": True
            })
    
    def _generate_magic_items(self, count=2):
        for _ in range(count):
            pos = self._get_valid_position()
            self.special_items.append({
                "position": pos,
                "image": self.special_item_images["magic"],
                "type": "magic",
                "active": True
            })
    
    def _generate_rescue_points(self, count=1):
        for _ in range(count):
            pos = self._get_valid_position()
            self.special_items.append({
                "position": pos,
                "image": self.special_item_images["rescue"],
                "type": "rescue",
                "active": True
            })
    
    def _generate_fog_zones(self, count=1):
        for _ in range(count):
            pos = self._get_valid_position()
            self.hazard_zones.append({
                "position": pos,
                "radius": 360,  # 从60改为120，迷雾范围扩大2倍
                "image": self.hazard_images["fog"],
                "type": "fog",
                "active": True
            })
    
    def _generate_lightning_zones(self, count=3):
        for _ in range(count):
            pos = self._get_valid_position()
            self.hazard_zones.append({
                "position": pos,
                "radius": 30,  # GRID_SIZE
                "image": self.hazard_images["lightning_zone"],
                "type": "lightning_zone",
                "active": True,
                "timer": 0
            })
    
    def _generate_lightning_strikes(self, count=4):
        for _ in range(count):
            pos = self._get_valid_position()
            self.moving_obstacles.append({
                "position": pos,
                "direction": (0, 1),  # DOWN
                "image": self.moving_images["lightning"],
                "timer": 0,
                "speed": 3.0,
                "type": "lightning",
                "active_time": random.randint(30, 60),
                "inactive_time": random.randint(30, 60),  # 从100-200改为30-60，更快显示
                "state": "inactive",
                "state_timer": 0
            })
    
    def _generate_fahai_boss(self):
        # BOSS的图片和渲染由boss.py负责，这里不再添加moving_obstacles
        pass
    
    def _generate_amulets(self, count=3):
        for _ in range(count):
            pos = self._get_valid_position()
            self.special_items.append({
                "position": pos,
                "image": self.special_item_images["amulet"],
                "type": "amulet",
                "active": True,
                "duration": 300
            })
    
    def _generate_random_amulet(self):
        """随机生成一个护身符"""
        pos = self._get_valid_position()
        self.special_items.append({
            "position": pos,
            "image": self.special_item_images["amulet"],
            "type": "amulet",
            "active": True,
            "duration": 300,
            "respawn_timer": 0  # 重生计时器
        })
    
    def _get_valid_position(self):
        max_attempts = 100
        for _ in range(max_attempts):
            x = random.randint(1, 38)  # GRID_WIDTH - 2
            y = random.randint(1, 28)  # GRID_HEIGHT - 2
            pos = (x, y)
            
            if not self._check_position_overlap(pos):
                return pos
        return (random.randint(1, 38), random.randint(1, 28))
    
    def _check_position_overlap(self, new_pos):
        new_x, new_y = new_pos
        for group in [self.positions, self.moving_obstacles, self.hazard_zones, self.special_items]:
            for obj in group:
                obj_x, obj_y = obj["position"]
                distance_sq = (new_x - obj_x)**2 + (new_y - obj_y)**2
                min_distance = 2
                if distance_sq < min_distance**2:
                    return True
        return False
    
    def update(self):
        for obs in self.moving_obstacles:
            obs["timer"] += obs["speed"]
            
            if obs["type"] == "lightning":
                obs["state_timer"] += 1
                if obs["state"] == "inactive" and obs["state_timer"] > obs["inactive_time"]:
                    obs["state"] = "active"
                    obs["state_timer"] = 0
                    obs["position"] = (random.randint(1, 38), 0)
                    obs["direction"] = (0, 1)  # DOWN
                elif obs["state"] == "active" and obs["state_timer"] > obs["active_time"]:
                    obs["state"] = "inactive"
                    obs["state_timer"] = 0
                    obs["position"] = (-10, -10)
                
                if obs["state"] == "active":
                    x, y = obs["position"]
                    dx, dy = obs["direction"]
                    obs["position"] = (x + dx, y + dy)
                    if y >= 30:  # GRID_HEIGHT
                        obs["state"] = "inactive"
                        obs["state_timer"] = 0
            else:
                if obs["timer"] >= 5:
                    obs["timer"] = 0
                    x, y = obs["position"]
                    dx, dy = obs["direction"]
                    new_x = (x + dx) % 40  # GRID_WIDTH
                    new_y = (y + dy) % 30  # GRID_HEIGHT
                    
                    if obs["type"] == "boss":
                        obs["attack_timer"] += 1
                        if obs["attack_timer"] >= obs["attack_interval"]:
                            obs["attack_timer"] = 0
                            if random.random() < 0.3:
                                obs["direction"] = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
                    
                    obs["position"] = (new_x, new_y)
                    if random.random() < 0.1:
                        obs["direction"] = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
        
        for zone in self.hazard_zones:
            if zone["type"] == "lightning_zone":
                zone["timer"] += 1
                zone["active"] = (zone["timer"] // 30) % 2 == 0
        
        # 护身符重生逻辑
        for item in self.special_items:
            if item.get("type") == "amulet" and not item.get("active", False):
                # 护身符被吃掉后，开始重生计时
                if "respawn_timer" not in item:
                    item["respawn_timer"] = 0
                item["respawn_timer"] += 1
                # 300帧后重新生成护身符
                if item["respawn_timer"] >= 300:
                    item["active"] = True
                    item["position"] = self._get_valid_position()
                    item["respawn_timer"] = 0
    
    def render(self, surface):
        # 第四关渲染前彻底过滤桥墩
        if getattr(self, 'current_level', None) == 4:
            self.positions = [obs for obs in self.positions if obs.get("type") != "bridge_pier"]
        for zone in self.hazard_zones:
            if zone["active"]:
                x, y = zone["position"]
                radius = zone.get("radius", 30)
                # 放大水域图片到radius*2大小
                img = zone["image"]
                big_img = pygame.transform.smoothscale(img, (radius*2, radius*2))
                img_rect = big_img.get_rect(
                    center=(x * GRID_SIZE + GRID_SIZE // 2,
                           y * GRID_SIZE + GRID_SIZE // 2)
                )
                surface.blit(big_img, img_rect)
        
        for obs in self.positions:
            x, y = obs["position"]
            img = obs["image"]
            if obs.get("center_pixel"):
                img_rect = img.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            else:
                img_rect = img.get_rect(center=(x * GRID_SIZE + GRID_SIZE // 2, y * GRID_SIZE + GRID_SIZE // 2))
            surface.blit(img, img_rect)
        
        for obs in self.moving_obstacles:
            if obs["type"] == "lightning" and obs["state"] != "active":
                continue
            x, y = obs["position"]
            img_rect = obs["image"].get_rect(
                center=(x * GRID_SIZE + GRID_SIZE // 2,
                       y * GRID_SIZE + GRID_SIZE // 2)
            )
            surface.blit(obs["image"], img_rect)
        
        for item in self.special_items:
            if item["active"]:
                x, y = item["position"]
                img_rect = item["image"].get_rect(
                    center=(x * GRID_SIZE + GRID_SIZE // 2,
                           y * GRID_SIZE + GRID_SIZE // 2)
                )
                surface.blit(item["image"], img_rect)
    
    def check_collision(self, position):
        px, py = position
        for obs in self.positions + self.moving_obstacles:
            if obs.get("type") == "lightning" and obs["state"] != "active":
                continue
                
            ox, oy = obs["position"]
            if (px == ox and py == oy):
                return True
        
        for zone in self.hazard_zones:
            if not zone["active"]:
                continue
                
            zx, zy = zone["position"]
            distance_sq = (px - zx)**2 + (py - zy)**2
            if distance_sq <= (zone.get("radius", 30) // 30 ** 2):  # GRID_SIZE
                return True
        
        return False
    
    def check_special_item_collision(self, position):
        px, py = position
        for item in self.special_items:
            if not item["active"]:
                continue
                
            ix, iy = item["position"]
            if (px == ix and py == iy):
                item["active"] = False
                return item["type"]
        return None
    
    def check_hazard_effect(self, position):
        px, py = position
        for zone in self.hazard_zones:
            if not zone["active"]:
                continue
                
            zx, zy = zone["position"]
            distance_sq = (px - zx)**2 + (py - zy)**2
            if distance_sq <= (zone.get("radius", 30) // 30 ** 2):  # GRID_SIZE
                return zone["type"]
        return None
    
    def is_boss_defeated(self):
        for obs in self.moving_obstacles:
            if obs["type"] == "boss" and obs.get("health", 0) <= 0:
                return True
        return False
    
    def advance_level(self):
        if self.current_level < 10:
            self.current_level += 1
            self.generate_level_obstacles()
            return True
        return False