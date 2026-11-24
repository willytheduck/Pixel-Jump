import math
import random
import pygame
from asset import sprite
from settings import *
import sound


class Enemy:
    sprite_name = "enemy.png"
    color = (200, 50, 50)
    w, h = 12, 12
    stompable = False

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.dead = False

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, camera, player=None):
        if self.y > camera + H + 40:
            self.dead = True

    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        surf.blit(img, (int(self.x), int(self.y - camera)))


class Burd(Enemy):
    sprite_name = "burd.png"
    color = (230, 200, 40)
    w, h = 16, 12
    stompable = True

    def __init__(self, x, y):
        super().__init__(x, y)
        self.dir = random.choice((-1, 1))
        self.sped = random.uniform(0.8, 1.6)

    def update(self, camera, player=None):
        super().update(camera, player)
        self.x += self.dir * self.sped
        if self.x < 0:
            self.x, self.dir = 0, 1
        elif self.x > W - self.w:
            self.x, self.dir = W - self.w, -1

    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        if self.dir < 0:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, (int(self.x), int(self.y - camera)))


class Rock(Enemy):
    sprite_name = "rock.png"
    color = (110, 110, 120)
    w, h = 10, 10

    def __init__(self, x, y):
        super().__init__(x, y)
        self.vy = 1.0

    def update(self, camera, player=None):
        super().update(camera, player)
        self.vy = min(self.vy + 0.05, 4.0)
        self.y += self.vy


class Bat(Enemy):
    sprite_name = "bat.png"
    color = (140, 70, 170)
    w, h = 14, 10
    TRIGGER = 120
    ALERT = 24
    SPED = 3.4

    def __init__(self, x, y):
        super().__init__(x, y)
        self.state = "idle"
        self.timer = 0
        self.t = random.uniform(0, 6.28)
        self.vx = 0.0
        self.vy = 0.0

    def update(self, camera, player=None):
        super().update(camera, player)
        if self.state == "idle":
            self.t += 0.1
            self.y += math.sin(self.t) * 0.3
            if player is not None and self.y > camera:
                below = player.y - self.y
                if 0 < below < self.TRIGGER and abs(player.x - self.x) < 110:
                    self.state = "alert"
                    self.timer = self.ALERT
                    sound.play("bat")
        elif self.state == "alert":
            self.x += random.uniform(-1, 1)
            self.timer -= 1
            if self.timer <= 0:
                if player is None:
                    self.state = "idle"
                    return
                dx = (player.x + PLAYER_W / 2) - (self.x + self.w / 2)
                dy = (player.y + PLAYER_H / 2) - (self.y + self.h / 2)
                dist = max(1.0, math.hypot(dx, dy))
                self.vx = dx / dist * self.SPED
                self.vy = dy / dist * self.SPED
                self.state = "dive"
        else:
            self.x += self.vx
            self.y += self.vy
            if self.x < -30 or self.x > W + 30:
                self.dead = True

    def draw(self, surf, camera):
        img = sprite(self.sprite_name, (self.w, self.h), self.color)
        if self.state == "dive" and self.vx < 0:
            img = pygame.transform.flip(img, True, False)
        surf.blit(img, (int(self.x), int(self.y - camera)))


KIND = {"bird": Burd, "rock": Rock, "bat": Bat}


def make_enemy(kind, x, y):
    return KIND[kind](x, y)
