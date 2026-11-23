import math
import random
import pygame
from enemy import make_enemy
from platforms import NPlatform, make_platform
from powerup import make_powerup
from particles import Particles
from player import Player
from settings import *
from shake import ScreenS
import sound
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
        self.bonus = 0
        self.combo = 0
        self.tick = 0
        self.dead = False
        self.death_cause = None
        self.won = False
        self.endless = False
        self.summit_place = False
        self.cur_zone = None
        self.notice = ""
        self.notice_sub = ""
        self.notice_timer = 0
        self.wind_now = 0.0
        self.shake = ScreenS()
        self.particles = Particles()
        self.platform = [NPlatform(W//2 - PLAT_W//2, H-30)]
        self.last_ly = self.platform[0].y
        self.enemy = []
        self.powerup = []
        self.gen_y = H -30
        self.generate()
    @property
    def zone(self):
        return get_zone(self.height)
    @property
    def score(self):
        return self.height + self.bonus
    def die(self,strength=6, frame=20, cause="fell"):
        if not self.dead:
            self.dead = True
            self.death_cause = cause
            self.shake.trigger(strength, frame)
            sound.play("fall" if cause == "fell" else "hit")
    def generate(self):
        while self.gen_y>self.camera-60:
            if self.summit_place and not self.endless: 
                break
            max_gap = min(50+self.height//100,80)
            self.gen_y -= random.randint(28,max_gap)
            h_at = int(self.start_y-self.gen_y)
            if h_at >= PEAK_HEIGHT and not self.summit_place:
                self.platform.append(make_platform("summit", W//2 - SUMMIT_W//2, self.gen_y))
                self.summit_place = True
                continue
            zone = get_zone(h_at)
            near_end = (not self.endless) and h_at > PEAK_HEIGHT - END_SAFE_ZONE
            x = random.randint(0,W-PLAT_W)
            kind_p = pick(zone.platform)
            self.platform.append(make_platform(kind_p, x, self.gen_y))
            if kind_p == "normal" and not near_end:
                if random.random() < JETPACK_CHANCE:
                    self.powerup.append(make_powerup("jetpack", x+(PLAT_W-10)//2, self.gen_y-12))
            if zone.enemies and random.random()<zone.enemy_c:
                kind = pick(zone.enemies)
                ex = random.randint(0,W-16)
                ey = self.camera - 20 if kind == "rock" else self.gen_y - 25
                self.enemy.append(make_enemy(kind,ex,ey))
    def on_landing(self, plat):
        p = self.player
        self.particles.burst(p.x + PLAYER_W/2, plat.y,plat.dust,plat.dust_n)
        if self.last_ly - plat.y >= COMBO_MIN_HOP:
            self.combo += 1
            if self.combo >= 2:
                self.bonus += COMBO_POINTS * self.combo
        else:
            self.combo = 0
        self.last_ly = plat.y
        sound.play(plat.sound)
        if self.combo >= 2:
            sound.play_combo(self.combo)
        if plat.summit and not self.endless:
            self.won = True

    def update(self, keys):
        if self.dead:
            return
        self.tick+=1
        p = self.player
        wind = self.zone.wind*math.sin(self.tick/90)
        self.wind_now = wind
        prev_btm = p.y +PLAYER_H
        p.update(keys,wind)
        new_btm = p.y + PLAYER_H
        for plat in self.platform:
            plat.update()
        for e in self.enemy:
            e.update(self.camera,p)
        for u in self.powerup:
            u.update(self.camera)
        surfaces = self.platform + [u for u in self.powerup if u.solid]
        if p.vy > 0: #for landing
            for plat in surfaces:
                if plat.dead:
                    continue
                overlap = p.x+PLAYER_W>plat.x and p.x<plat.x+plat.w
                if overlap and prev_btm <= plat.y and new_btm>=plat.y:
                    p.y=plat.y-PLAYER_H
                    if getattr(plat, "deadly", False):
                        self.die(6,20,"landed on spikes")
                        break
                    p.vy = plat.on_land(p)
                    if hasattr(plat, "summit"):
                        self.on_landing(plat)
                    if plat.shake:
                        self.shake.trigger(*plat.shake)
                    break
        for u in self.powerup: #for collectible
            if u.collectible and not u.dead and p.rect.colliderect(u.rect):
                u.on_collect(p,self)
        if p.jetpack > 0:
            self.shake.trigger(1,3)
        for e in self.enemy:
            if p.jetpack > 0:
                break
            if e.dead or not p.rect.colliderect(e.rect):
                continue
            if e.stompable and p.vy > 0 and prev_btm <= e.y + 6:
                e.dead = True
                p.vy = STOMP_BOUNCE
                self.bonus += STOMP_POINTS
                sound.play("stomp")
                self.shake.trigger(3,8)
            else:
                self.die(6,20,"Hit by a "+ type(e).__name__)
        if p.y - self.camera < H*CAMERA_LINE:
            self.camera = p.y-H*CAMERA_LINE
        self.height = max(self.height,int(self.start_y-p.y))
        self.best = max(self.best, self.score)
        
        #zone popup
        z = self.zone
        if z.name != self.cur_zone:
            if self.cur_zone is not None:
                sound.play("zone")
            self.cur_zone = z.name
            self.notice = z.name
            self.notice_sub = f"{z.start}m"
            self.notice_timer = NOTICE_FRAME
        if self.notice_timer >0:
            self.notice_timer -= 1
        self.particles.update(wind, z.wind)
        self.generate()
        self.platform=[q for q in self.platform if not q.dead and q.y < self.camera + H + 20]
        self.enemy = [e for e in self.enemy if not e.dead]
        self.powerup = [u for u in self.powerup if not u.dead and u.y < self.camera + H + 20]
        if p.y - self.camera > H:
            self.die(4,15)

    def draw(self,surf):
        surf.fill(sky_color(self.height))
        self.particles.draw_wind(surf)
        for plat in self.platform:
            plat.draw(surf,self.camera)
        for u in self.powerup:
            u.draw(surf,self.camera)
        for e in self.enemy:
            e.draw(surf,self.camera)
        self.player.draw(surf,self.camera)
        self.particles.draw_dust(surf,self.camera)