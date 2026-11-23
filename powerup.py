import pygame
from asset import sprite
from settings import *
import sound
class PowerUp:
    sprite_name = "powerup.png"
    color = (255,0,255)
    w,h = 10, 10
    solid = False
    collectible = False
    shake = None
    def __init__(self,x,y):
        self.x=float(x)
        self.y=float(y)
        self.dead = False
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w,self.h)
    def update(self,camera):
        if self.y > camera + H+40:
            self.dead = True
    def on_land(self,player):
        return JUMP
    def on_collect(self,player,world):
        pass
    def draw(self,surf,camera):
        img = sprite(self.sprite_name,(self.w,self.h),self.color)
        surf.blit(img,(int(self.x),int(self.y-camera)))

class Jetpack(PowerUp):
    sprite_name = "jetpack_item.png"
    color = (150,150,170)
    w,h = 10,12
    collectible = True

    def on_collect(self,player,world):
        player.jetpack = JETPACK_FRAMES
        self.dead = True
        world.shake.trigger(3,10)
        sound.play("pickup")

KIND = {"jetpack": Jetpack}
def make_powerup(kind,x,y):
    return KIND[kind](x,y)