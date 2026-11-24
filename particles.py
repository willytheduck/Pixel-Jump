import random
import pygame
from settings import *


class Particles:
    def __init__(self):
        self.dust = []  # world coordinates
        self.streaks = []  # screen coordinates

    def burst(self, x, y, color, n=5):
        for _ in range(n):
            self.dust.append(
                [
                    x + random.uniform(-5, 5),
                    y,
                    random.uniform(-1.2, 1.2),
                    random.uniform(-1.4, -0.3),
                    random.randint(14, 26),
                    color,
                ]
            )

    def update(self, wind_now, zone_wind):
        for d in self.dust:
            d[0] += d[2]
            d[1] += d[3]
            d[3] += 0.08
            d[4] -= 1
        self.dust = [d for d in self.dust if d[4] > 0]

        # wind streak
        if zone_wind > 0:
            strength = min(1.0, abs(wind_now) / zone_wind)
            if (
                random.random() < 0.7 * strength
                and len(self.streaks) < MAX_WIND_STREAKS
            ):
                vx = wind_now * 14
                start_x = -10 if vx > 0 else W + 10
                self.streaks.append(
                    [start_x, random.uniform(0, H), vx, int(abs(vx) * 1.5) + 2]
                )
        for s in self.streaks:
            s[0] += s[2]
        self.streaks = [s for s in self.streaks if -40 < s[0] < W + 40]

    def draw_wind(self, surf):
        for x, y, vx, length in self.streaks:
            tail = x - length if vx > 0 else x + length
            pygame.draw.line(
                surf, (225, 235, 245), (int(tail), int(y)), (int(x), int(y)), 1
            )

    def draw_dust(self, surf, camera):
        for x, y, vx, vy, life, color in self.dust:
            size = 2 if life > 10 else 1
            pygame.draw.rect(surf, color, (int(x), int(y - camera), size, size))
