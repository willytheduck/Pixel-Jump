import random
from settings import SHAKE_ENABLE
class ScreenS:
    def __init__(self):
        self.strength = 0.0
        self.frame = 0
        self.total = 1
    def current(self):
        if self.frame <= 0:
            return 0.0
        return self.strength*self.frame/self.total
    def trigger(self,strength, frame):
        if not SHAKE_ENABLE:
            return
        if strength >= self.current(): #to not let the weak shake cutting off the stronger one
            self.strength = strength
            self.frame = frame
            self.total = frame
    def update(self):
        if self.frame <= 0:
            return 0.0,0.0
        amount = self.current()
        self.frame -= 1
        return random.uniform(-amount,amount),random.uniform(-amount,amount)
