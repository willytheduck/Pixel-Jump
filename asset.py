import os
import pygame
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
_cache = {}

def sprite(name, size, color):
    if name in _cache:
        return _cache[name]
    path = os.path.join(ASSETS_DIR, name)
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = img.convert_alpha() if pygame.display.get_surface() else img
    else:
        img = pygame.Surface(size)
        img.fill(color)
    _cache[name] = img
    return img
