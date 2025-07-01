import pygame

def load_chinese_font(size):
    # 使用系统自带的黑体字体，无需下载字体文件
    return pygame.font.SysFont("SimHei", size)