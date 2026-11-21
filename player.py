import pygame

from asset import sprite
from settings import *

class Player:
    def __init__(self,x,y):
        self.x = float(x)
        self.y = float(y)
        self.vy = JUMP
        self.facing = 1

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), PLAYER_W, PLAYER_H)

    def update(self,keys, wind=0.0):
        dx = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= SPED
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += SPED
        if dx:
            self.facing = 1 if dx > 0 else -1
        self.x += dx + wind
        if self.x < -PLAYER_W:
            self.x = W
        elif self.x > W:
            self.x = -PLAYER_W
        self.vy += GRAV
        self.y += self.vy

    def draw(self,surf,camera):
        img = sprite("player.png", (PLAYER_W,PLAYER_H), (240,120,60))
        if self.facing < 0:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, (int(self.x), int(self.y - camera)))
        