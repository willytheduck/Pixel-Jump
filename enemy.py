import random
import pygame
from asset import sprite
from settings import *

class Enemy:
    sprite_name = "enemy.png"
    color = (200,50,50)
    w,h = 12,12
    stompable = False
    def __init__(self,x,y):
        self.x = float(x)
        self.y = float(y)
        self.dead = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self,camera):
        if self.y > camera +H+40:
            self.dead = True

    def draw(self,surf,camera):
        img = sprite(self.sprite_name, (self.w,self.h),self.color)
        surf.blit(img, (int(self.x), int(self.y - camera)))


class Burd(Enemy):
    sprite_name = "burd.png"
    color = (230,200,40)
    w,h = 16,12
    stompable = True

    def __init__(self,x,y):
        super().__init__(x,y)
        self.dir = random.choice((-1,1))
        self.sped = random.uniform(0.8,1.6)

    def update(self,camera):
        super().update(camera)
        self.x += self.dir *self.sped
        if self.x < 0:
            self.x, self.dir = 0, 1
        elif self.x>W-self.w:
            self.x, self.dir = W - self.w, -1

    def draw(self,surf,camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        if self.dir < 0:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img,(int(self.x), int(self.y-camera)))

class Rock(Enemy):
    sprite_name = "rock.png"
    color = (110,110,120)
    w, h = 10,10

    def __init__(self,x,y):
        super().__init__(x,y)
        self.vy = 1.0
    def update(self,camera):
        super().update(camera)
        self.vy = min(self.vy + 0.05, 4.0)
        self.y += self.vy

KIND = {"bird": Burd, "rock": Rock}

def make_enemy(kind, x, y):
    return KIND[kind](x,y)