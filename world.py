import math
import random
import pygame
from enemy import make_enemy
from platforms import NPlatform, make_platform
from player import Player
from settings import *
from zones import get_zone, pick, sky_color

class World:
    def __init__(self):
        self.best = 0
        self.reset()
    def reset(self):
        self.player = Player(W/2-PLAYER_W/2,H-50.0)
        self.start_y = self.player.y
        self.camera = 0.0
        self.height = 0
        self.dead = False
        self.reach_peak = False
        self.tick = 0
        self.platform = [NPlatform(W//2 - PLAT_W//2, H-30)]
        self.enemy = []
        self.gen_y = H -30
        self.generate()
    @property
    def zone(self):
        return get_zone(self.height)
    def generate(self):
        while self.gen_y>self.camera-60:
            max_gap = min(50+self.height//100,80)
            self.gen_y -= random.randint(28,max_gap)
            zone = get_zone(int(self.start_y-self.gen_y))
            x = random.randint(0,W-PLAT_W)
            self.platform.append(make_platform(pick(zone.platform), x,self.gen_y))
            if zone.enemies and random.random()<zone.enemy_c:
                kind = pick(zone.enemies)
                ex = random.randint(0,W-16)
                ey = self.camera - 20 if kind == "rock" else self.gen_y - 25
                self.enemy.append(make_enemy(kind,ex,ey))
    def update(self, keys):
        if self.dead:
            return
        self.tick+=1
        p = self.player
        wind = self.zone.wind*math.sin(self.tick/90)
        prev_btm = p.y +PLAYER_H
        p.update(keys,wind)
        new_btm = p.y + PLAYER_H
        for plat in self.platform:
            plat.update()
        for e in self.enemy:
            e.update(self.camera)
        if p.vy > 0: #for landing
            for plat in self.platform:
                if plat.dead:
                    continue
                overlap = p.x+PLAYER_W>plat.x and p.x<plat.x+plat.w
                if overlap and prev_btm <= plat.y and new_btm>=plat.y:
                    p.y=plat.y-PLAYER_H
                    p.vy = plat.on_land(p)
                    break
        for e in self.enemy:
            if e.dead or not p.rect.colliderect(e.rect):
                continue
            if e.stompable and p.vy > 0 and prev_btm <= e.y + 6:
                e.dead = True
                p.vy = STOMP_BOUNCE
            else:
                self.dead = True
        if p.y - self.camera < H*CAMERA_LINE:
            self.camera = p.y-H*CAMERA_LINE
        self.height = max(self.height,int(self.start_y-p.y))
        self.best = max(self.best, self.height)
        if self.height >= PEAK_HEIGHT:
            self.reach_peak = True
        self.generate()
        self.platform=[q for q in self.platform if not q.dead and q.y < self.camera + H + 20]
        self.enemy = [e for e in self.enemy if not e.dead]
        if p.y - self.camera > H:
            self.dead = True

    def draw(self,surf):
        surf.fill(sky_color(self.height))
        for plat in self.platform:
            plat.draw(surf,self.camera)
        for e in self.enemy:
            e.draw(surf,self.camera)
        self.player.draw(surf,self.camera)