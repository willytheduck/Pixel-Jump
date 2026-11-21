import random

from asset import sprite
from settings import *

class Platform:
    sprite_name = "platform.png"
    color = (90,160,80)
    def __init__(self,x,y):
        self.x = float(x)
        self.y = float(y)
        self.w = PLAT_W
        self.h = PLAT_H
        self.dead = False

    def update(self):
        pass

    def on_land(self,player):
        return JUMP

    def draw(self, surf, camera):
        img = sprite(self.sprite_name,(self.w, self.h), self.color)
        surf.blit(img, (int(self.x), int(self.y - camera)))

class NPlatform(Platform):
    pass

class MPlatform(Platform):
    sprite_name= "platform_move.png"
    color = (80,120,200)

    def __init__(self,x,y):
        super().__init__(x,y)
        self.dir = random.choice((-1,1))
        self.sped = random.uniform(0.6,1.4)
    def update(self):
        self.x += self.dir * self.sped
        if self.x < 0:
            self.x, self.dir = 0,1
        elif self.x > W - self.w:
            self.x, self.dir = W - self.w, -1

class CPlatform(Platform):
    sprite_name = "platform_crumble.png"
    color = (190,225,245)
    def __init__(self,x,y):
        super().__init__(x,y)
        self.timer = None
    def on_land(self,player):
        if self.timer is None:
            self.timer = 15
        return JUMP
    def update(self):
        if self.timer is not None:
            self.timer -= 1
            if self.timer <= 0:
                self.dead = True
    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        jitter = random.randint(-1,1) if self.timer is not None else 0
        surf.blit(img, (int(self.x) + jitter, int(self.y - camera)))

class SPlatform(Platform):
    sprite_name = "platform_spring.png"
    color = (220,80,80)

    def on_land(self,player):
        return SPRING_JUMP

KIND = {
    "normal": NPlatform,
    "moving": MPlatform,
    "crumble": CPlatform,
    "spring": SPlatform,
}

def make_platform(kind,x,y):
    return KIND[kind](x,y)
    