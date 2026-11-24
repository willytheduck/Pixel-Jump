import os
import random
import pygame

from asset import sprite, ASSETS_DIR
from settings import *
import sound


class Platform:
    sprite_name = "platform.png"
    color = (90, 160, 80)
    shake = None
    deadly = False
    summit = False
    dust = (190, 180, 150)
    dust_n = 5
    sound = "jump"

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = PLAT_W
        self.h = PLAT_H
        self.dead = False

    def update(self):
        pass

    def on_land(self, player):
        return JUMP

    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        surf.blit(img, (int(self.x), int(self.y - camera)))


class NPlatform(Platform):
    dust = (150, 190, 110)


class MPlatform(Platform):
    sprite_name = "platform_move.png"
    color = (80, 120, 200)
    dust = (130, 160, 220)

    def __init__(self, x, y):
        super().__init__(x, y)
        self.dir = random.choice((-1, 1))
        self.sped = random.uniform(0.6, 1.4)

    def update(self):
        self.x += self.dir * self.sped
        if self.x < 0:
            self.x, self.dir = 0, 1
        elif self.x > W - self.w:
            self.x, self.dir = W - self.w, -1


class CPlatform(Platform):
    sprite_name = "platform_crumble.png"
    color = (190, 225, 245)
    dust = (200, 230, 250)

    def __init__(self, x, y):
        super().__init__(x, y)
        self.timer = None

    def on_land(self, player):
        if self.timer is None:
            self.timer = 15
        return JUMP

    def update(self):
        if self.timer is not None:
            self.timer -= 1
            if self.timer <= 0 and not self.dead:
                self.dead = True
                sound.play("crack")

    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        jitter = random.randint(-1, 1) if self.timer is not None else 0
        surf.blit(img, (int(self.x) + jitter, int(self.y - camera)))


class TPlatform(Platform):
    sprite_name = "platform_trampoline.png"
    color = (220, 80, 80)
    shake = (2, 8)
    sound = "boing"
    dust = (240, 130, 130)
    dust_n = 10

    def on_land(self, player):
        return TRAMP_JUMP


class SPlatform(Platform):
    sprite_name = "platform_spike.png"
    color = (130, 130, 150)
    deadly = True
    dust = (150, 150, 150)


class STPlatform(Platform):
    sprite_name = "platform_summit.png"
    color = (240, 200, 60)
    summit = True
    dust = (255, 230, 120)
    dust_n = 10

    def __init__(self, x, y):
        super().__init__(x, y)
        self.w = SUMMIT_W

    def draw(self, surf, camera):
        super().draw(surf, camera)
        fx = int(self.x + self.w / 2)
        fy = int(self.y - camera)
        if os.path.exists(os.path.join(ASSETS_DIR, "flag.png")):
            surf.blit(sprite("flag.png", (12, 22), (230, 60, 60)), (fx - 6, fy - 22))
        else:
            pygame.draw.rect(surf, (230, 230, 230), (fx, fy - 22, 2, 22))
            pygame.draw.polygon(
                surf,
                (230, 60, 60),
                [(fx + 2, fy - 22), (fx + 14, fy - 17), (fx + 2, fy - 12)],
            )


KIND = {
    "normal": NPlatform,
    "moving": MPlatform,
    "crumble": CPlatform,
    "trampoline": TPlatform,
    "spike": SPlatform,
    "summit": STPlatform,
}


def make_platform(kind, x, y):
    return KIND[kind](x, y)
