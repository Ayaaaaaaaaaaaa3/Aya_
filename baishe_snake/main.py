import pygame
from snake import Snake
from food import Food
from map import GameMap
from boss import Boss
from skill import SkillTree
from utils import load_chinese_font
import math
import random

pygame.init()
cell_size = 20
width, height = 40, 30  # 格子数
screen = pygame.display.set_mode((width*cell_size, height*cell_size))
pygame.display.set_caption("白蛇贪吃劫")
font = load_chinese_font(32)
title_font = load_chinese_font(48)
tip_font = load_chinese_font(28)

# 关卡数据
levels = [
    {"name": "西湖初遇", "fruit_name": "青蛇果", "target": 1, "obstacles": None, "special": None},
    {"name": "断桥相会", "fruit_name": "莲花果", "target": 1, "obstacles": "bridge", "special": None},
    {"name": "金山寺门前", "fruit_name": "灵芝果", "target": 1, "obstacles": "monk", "special": "moving_obstacle"},
    {"name": "雷峰塔下", "fruit_name": "仙草果", "target": 1, "obstacles": "narrow", "special": "fast"},
    {"name": "水漫金山", "fruit_name": "水灵果", "target": 2, "obstacles": None, "special": "water"},
    {"name": "白蛇斗法", "fruit_name": "法力果", "target": 1, "obstacles": None, "special": "invincible"},
    {"name": "小青救主", "fruit_name": "青藤果", "target": 1, "obstacles": None, "special": "rescue"},
    {"name": "迷雾幻境", "fruit_name": "幻境果", "target": 1, "obstacles": None, "special": "fog"},
    {"name": "天降雷罚", "fruit_name": "雷电果", "target": 1, "obstacles": None, "special": "thunder"},
    {"name": "终极BOSS 法海", "fruit_name": "佛珠果", "target": 2, "obstacles": "boss", "special": "boss_final"}
]

current_level = 0
fruit_eaten = 0

# 速度调节参数
speed_offset = 10  # 可调节的速度偏移量
min_speed = 1
max_speed = 30

# 游戏数据初始化函数
def start_level(level_idx):
    global snake, game_map, food, skill_tree, boss, score, level, clock, time_limit, start_ticks, speed_offset, fruit_eaten
    snake = Snake()
    game_map = GameMap(width, height)
    # 设置障碍
    if levels[level_idx]["obstacles"]:
        game_map.set_obstacles(levels[level_idx]["obstacles"])
    else:
        game_map.obstacles = []
    food = Food(width, height, snake.body, game_map.obstacles, fruit_name=levels[level_idx]["fruit_name"])
    skill_tree = SkillTree()
    boss = None
    score = 0
    level = level_idx + 1
    clock = pygame.time.Clock()
    time_limit = 60  # 每关时间限制（秒）
    start_ticks = pygame.time.get_ticks()
    speed_offset = 10
    fruit_eaten = 0

max_score = 0
start_level(0)
paused = False

# 加载主界面背景图片（如有）
try:
    bg_img = pygame.image.load(r"E:/github/AYA_/baishe_snake/start.jpg")
    bg_img = pygame.transform.scale(bg_img, (width*cell_size, height*cell_size))
except:
    bg_img = None

game_state = "start"

# 新增：第十关护身符管理
def spawn_amulet(game_map):
    # 随机生成护身符位置，不能和障碍重叠
    while True:
        pos = (random.randint(0, width-1), random.randint(0, height-1))
        if pos not in game_map.obstacles:
            return pos

amulet_pos = None
amulet_count = 0
boss_weak = False
boss_circle_goal = 3

# 加载Boss图片（如有）
boss_img_path = r"E:/github/AYA_/baishe_snake/boss.png"
boss_img = None
try:
    boss_img = pygame.image.load(boss_img_path)
    boss_img = pygame.transform.scale(boss_img, (cell_size, cell_size))
    print(f"Boss图片加载成功: {boss_img_path}")
except Exception as e:
    boss_img = None
    print(f"Boss图片加载失败: {boss_img_path}, 错误: {e}")

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            if game_state == "start" and event.key == pygame.K_SPACE:
                game_state = "playing"
                start_level(current_level)
                amulet_pos = None
                amulet_count = 0
                boss_weak = False
            elif game_state == "gameover" and event.key == pygame.K_SPACE:
                game_state = "start"
            elif game_state == "playing" and not paused:
                if event.key == pygame.K_UP:
                    snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.change_direction((1, 0))
                elif event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    speed_offset = min(max_speed, speed_offset + 1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed_offset = max(min_speed, speed_offset - 1)

    # 防止current_level越界，通关后直接进入结束界面
    if current_level >= len(levels):
        game_state = "gameover"
        msg = "恭喜通关！"
        screen.fill((0, 0, 0))
        screen.blit(title_font.render(msg, True, (255, 215, 0)), (width*cell_size//2-180, height*cell_size//3))
        screen.blit(font.render(f"最高分：{max_score}", True, (255,255,255)), (width*cell_size//2-60, height*cell_size//2+50))
        screen.blit(tip_font.render("按空格返回开始界面", True, (255,0,0)), (width*cell_size//2-180, height*cell_size//2+120))
        pygame.display.flip()
        continue

    if paused and game_state == "playing":
        screen.blit(title_font.render("暂停中", True, (255, 255, 0)), (width*cell_size-220, 10))
        pygame.display.flip()
        continue

    # 关卡特殊机制动态更新
    special = levels[current_level]["special"]
    if special == "moving_obstacle":
        game_map.update_moving_obstacles()
    if special == "water":
        game_map.update_water_areas()
    if special == "thunder":
        game_map.update_thunder_zones()

    # 第十关护身符定期刷新
    if special == "boss_final":
        if amulet_pos is None and random.random() < 0.01:
            amulet_pos = spawn_amulet(game_map)

    if game_state == "start":
        if bg_img:
            screen.blit(bg_img, (0, 0))
        else:
            screen.fill((0, 0, 0))
        screen.blit(title_font.render("白蛇贪吃劫", True, (0,255,0)), (width*cell_size//2-180, height*cell_size//3))
        screen.blit(tip_font.render("按空格开始游戏", True, (255,255,255)), (width*cell_size//2-150, height*cell_size//2))
        pygame.display.flip()
        continue

    if game_state == "playing" and not paused:
        snake.move()
        skill_tree.update()
        # 关卡特殊机制判定
        if special == "boss_final" and boss and boss_weak:
            # 只检测撞墙和障碍物，忽略自撞
            head = snake.body[0]
            if head[0] < 0 or head[0] >= width or head[1] < 0 or head[1] >= height:
                hit_obstacle = True
            elif head in game_map.obstacles:
                hit_obstacle = True
            else:
                hit_obstacle = False
        else:
            hit_obstacle = snake.check_collision(width, height, game_map.obstacles)
        # 3关和尚巡逻
        if special == "moving_obstacle":
            if snake.body[0] in game_map.moving_obstacles:
                hit_obstacle = True
        # 5关水区减速
        in_water = False
        if special == "water" and snake.body[0] in game_map.water_areas:
            in_water = True
        # 7关救援点
        rescue_score = 0
        if special == "rescue" and snake.body[0] in game_map.rescue_points:
            rescue_score += 5
            game_map.rescue_points.remove(snake.body[0])
        # 8关迷雾区
        in_fog = False
        if special == "fog" and snake.body[0] in game_map.fog_areas:
            in_fog = True
        # 9关雷电
        hit_thunder = False
        if special == "thunder" and snake.body[0] in game_map.thunder_zones:
            hit_thunder = True
        # 10关法球碰撞
        hit_ball = False
        if special == "boss_final" and boss and boss.alive:
            hit_ball = boss.check_ball_hit(snake.body)
        # 10关护身符拾取
        if special == "boss_final" and amulet_pos and snake.body[0] == amulet_pos:
            amulet_count += 1
            amulet_pos = None
        # 10关吃满佛珠果后BOSS虚弱
        if special == "boss_final" and fruit_eaten >= levels[current_level]["target"] and boss and not boss_weak:
            boss.set_weak(True)
            boss_weak = True
        # 10关BOSS虚弱后绕圈
        if special == "boss_final" and boss and boss_weak:
            boss.update_circle(snake.body[0])
            if boss.circle_count >= boss_circle_goal:
                game_state = "gameover"
                msg = "最终胜利！你完成了三圈挑战！"
                continue
        # 碰撞判定
        if hit_obstacle or hit_thunder or hit_ball:
            if special == "invincible" and skill_tree.is_invincible():
                pass
            elif special == "boss_final" and hit_ball and amulet_count > 0:
                amulet_count -= 1  # 护身符抵消一次法球
                boss.balls = []
            else:
                game_state = "gameover"
                max_score = max(max_score, score)
        # 吃食物
        if snake.body[0] == food.position:
            fruit_eaten += 1
            if food.type == "normal":
                score += 1
                snake.eat()
                skill_tree.gain_exp(1)
            elif food.type == "special":
                score += 2
                snake.eat()
                skill_tree.gain_exp(2)
                if special == "invincible":
                    skill_tree.use_skill("invincible", duration=150)
            elif food.type == "positive":
                pass
            elif food.type == "negative":
                pass
            food.respawn(snake.body, game_map.obstacles)
        if special == "rescue" and rescue_score > 0:
            score += rescue_score
        # 关卡目标判定
        if special == "boss_final":
            # 只在BOSS虚弱且绕圈完成后才通关
            if boss and boss_weak and boss.circle_count >= boss_circle_goal:
                current_level += 1
                if current_level < len(levels):
                    start_level(current_level)
                    amulet_pos = None
                    amulet_count = 0
                    boss_weak = False
                else:
                    game_state = "gameover"
                    msg = "恭喜通关！"
                    continue
        else:
            if fruit_eaten >= levels[current_level]["target"]:
                current_level += 1
                if current_level < len(levels):
                    start_level(current_level)
                    amulet_pos = None
                    amulet_count = 0
                    boss_weak = False
                else:
                    game_state = "gameover"
                    msg = "恭喜通关！"
                    continue
        if levels[current_level]["special"] == "boss_final" and boss is None:
            boss = Boss(width // 2, height // 2, cell_size, image_path=boss_img_path if boss_img else None)
            boss.set_mode("final")
        if boss and boss.alive:
            boss.move(width, height, game_map.obstacles, target_pos=snake.body[0])
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        if seconds > time_limit:
            game_state = "gameover"

    # 游戏结束界面
    if game_state == "gameover":
        screen.fill((0, 0, 0))
        if current_level >= len(levels):
            msg = "恭喜通关！"
        elif boss and boss.alive == False:
            msg = "胜利！你打败了法海！"
        else:
            msg = "游戏结束"
        screen.blit(title_font.render(msg, True, (255, 215, 0)), (width*cell_size//2-180, height*cell_size//3))
        screen.blit(font.render(f"得分：{score}", True, (255,255,255)), (width*cell_size//2-60, height*cell_size//2))
        screen.blit(font.render(f"最高分：{max_score}", True, (255,255,255)), (width*cell_size//2-60, height*cell_size//2+50))
        screen.blit(tip_font.render("按空格返回开始界面", True, (255,0,0)), (width*cell_size//2-180, height*cell_size//2+120))
        pygame.display.flip()
        continue

    # 渲染
    screen.fill((200, 255, 240))  # 浅薄荷绿
    screen.blit(font.render(f"第{level}关 {levels[current_level]['name']}  {fruit_eaten}/{levels[current_level]['target']} {levels[current_level]['fruit_name']}", True, (255,255,255)), (10, 10))
    if special == "invincible" and skill_tree.is_invincible():
        screen.blit(font.render(f"无敌中 剩余:{skill_tree.invincible_timer}", True, (255,255,0)), (10, 130))
    if special == "moving_obstacle":
        for x, y in game_map.moving_obstacles:
            pygame.draw.rect(screen, (200, 180, 80), (x*cell_size, y*cell_size, cell_size, cell_size))
    if special == "water":
        for x, y in game_map.water_areas:
            pygame.draw.rect(screen, (0, 128, 255), (x*cell_size, y*cell_size, cell_size, cell_size))
    if special == "rescue":
        for x, y in game_map.rescue_points:
            pygame.draw.circle(screen, (255, 0, 255), (x*cell_size+cell_size//2, y*cell_size+cell_size//2), cell_size//2)
    if special == "fog":
        fog_surf = pygame.Surface((width*cell_size, height*cell_size), pygame.SRCALPHA)
        for x, y in game_map.fog_areas:
            pygame.draw.rect(fog_surf, (50, 50, 50, 180), (x*cell_size, y*cell_size, cell_size, cell_size))
        screen.blit(fog_surf, (0, 0))
    if special == "thunder":
        for x, y in game_map.thunder_zones:
            pygame.draw.line(screen, (255,255,0), (x*cell_size+cell_size//2, 0), (x*cell_size+cell_size//2, height*cell_size), 2)
            pygame.draw.circle(screen, (255,255,0), (x*cell_size+cell_size//2, y*cell_size+cell_size//2), cell_size//2, 2)
    # 10关护身符
    if special == "boss_final" and amulet_pos:
        pygame.draw.circle(screen, (0,255,255), (amulet_pos[0]*cell_size+cell_size//2, amulet_pos[1]*cell_size+cell_size//2), cell_size//2)
    # 10关护身符数量
    if special == "boss_final":
        screen.blit(font.render(f"护身符：{amulet_count}", True, (0,255,255)), (10, 160))
    # 10关BOSS虚弱与绕圈
    if special == "boss_final" and boss and boss_weak:
        screen.blit(font.render(f"BOSS虚弱，绕圈进度：{boss.circle_count}/{boss_circle_goal}", True, (255,0,0)), (10, 190))
    # 画蛇
    head_x, head_y = snake.body[0]
    center = (head_x*cell_size + cell_size//2, head_y*cell_size + cell_size//2)
    pygame.draw.circle(screen, (255, 255, 255), center, cell_size//2)
    eye_radius = cell_size // 7
    eye_offset_x = cell_size // 5
    eye_offset_y = cell_size // 5
    dx, dy = snake.direction
    if dx == 1:
        eye1 = (center[0] + eye_offset_x, center[1] - eye_offset_y)
        eye2 = (center[0] + eye_offset_x, center[1] + eye_offset_y)
    elif dx == -1:
        eye1 = (center[0] - eye_offset_x, center[1] - eye_offset_y)
        eye2 = (center[0] - eye_offset_x, center[1] + eye_offset_y)
    elif dy == 1:
        eye1 = (center[0] - eye_offset_x, center[1] + eye_offset_y)
        eye2 = (center[0] + eye_offset_x, center[1] + eye_offset_y)
    else:
        eye1 = (center[0] - eye_offset_x, center[1] - eye_offset_y)
        eye2 = (center[0] + eye_offset_x, center[1] - eye_offset_y)
    pygame.draw.circle(screen, (0,0,0), eye1, eye_radius)
    pygame.draw.circle(screen, (0,0,0), eye2, eye_radius)
    for x, y in snake.body[1:]:
        center = (x*cell_size + cell_size//2, y*cell_size + cell_size//2)
        pygame.draw.circle(screen, (255, 255, 255), center, cell_size//2)
    color = (255, 0, 0) if food.type == "normal" else (255, 255, 0)
    pygame.draw.rect(screen, color, (food.position[0]*cell_size, food.position[1]*cell_size, cell_size, cell_size))
    for x, y in game_map.obstacles:
        pygame.draw.rect(screen, (128, 128, 128), (x*cell_size, y*cell_size, cell_size, cell_size))
    screen.blit(font.render(f"得分：{score}  最高分：{max_score}", True, (255,255,255)), (10, 40))
    screen.blit(font.render(f"当前速度：{speed_offset}", True, (0,255,255)), (10, 90))
    if game_state == "playing":
        seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        screen.blit(font.render(f"剩余时间：{max(0, time_limit - seconds)}秒", True, (255,255,0)), (10, 60))
    pygame.display.flip()
    if game_state == "playing" and not paused:
        if special == "water" and in_water:
            clock.tick(8)
        elif special == "fast":
            clock.tick(snake.speed + score // 5 + speed_offset + 10)
        else:
            clock.tick(snake.speed + score // 5 + speed_offset)

    # BOSS渲染放到最后，确保不会被覆盖
    if boss and boss.alive:
        boss.draw(screen)

pygame.quit()
