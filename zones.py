from dataclasses import dataclass, field
import random

@dataclass
class Zone:
    name: str
    start: int
    sky: tuple
    platform: dict
    enemy_c: float = 0.0
    enemies: dict = field(default_factory=dict)
    wind: float = 0.0

ZONE = [
    Zone("Forest", 0, (150, 200, 240),
         {"normal": 8, "moving": 2, "spring": 1}, 0.05, {"bird": 1}),
    Zone("Alpine", 1000, (120, 160, 210),
         {"normal": 6, "moving": 3, "crumble": 2, "spring": 1}, 0.10, {"bird": 1}),
    Zone("Snow", 2500, (190, 205, 225),
         {"normal": 5, "moving": 3, "crumble": 3, "spring": 1}, 0.12, {"bird": 2, "rock": 1}),
    Zone("Storm", 4000, (60, 60, 90),
         {"normal": 4, "moving": 3, "crumble": 4, "spring": 1}, 0.18, {"bird": 2, "rock": 2}, 0.5),
    Zone("Summit", 5000, (20, 20, 50),
         {"normal": 4, "moving": 3, "crumble": 4, "spring": 1}, 0.20, {"bird": 2, "rock": 2}, 0.6),
]

def get_zone(height):
    zone = ZONE[0]
    for z in ZONE:
        if height >= z.start:
            zone = z
    return zone

def _lerp(a,b,t):
    t = max(0.0, min(1.0,t))
    return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def sky_color(height):
    for i, z in enumerate(ZONE):
        if i + 1 < len(ZONE) and height < ZONE[i+1].start:
            nxt = ZONE[i+1]
            return _lerp(z.sky,nxt.sky,(height-z.start)/(nxt.start-z.start))
    return ZONE[-1].sky

def pick(weights):
    return random.choices(list(weights.keys()), weights=list(weights.values()))[0]
