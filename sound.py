import array
import math
import os
import random
import pygame
from settings import *
from paths import resource_path

SOUND_DIR = resource_path("sounds")
_cache = {}
_ready = False
_synth_ok = False
_muted = False
_rate = 44100
_channels = 2


def init():
    global _ready, _synth_ok, _rate, _channels
    if not SOUND_ENABLED:
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        info = pygame.mixer.get_init()
        if info is None:
            return
        _rate, size, _channels = info
        _synth_ok = size == -16
        _ready = True
    except pygame.error:
        _ready = False


# tiny synthesizer
def _wave(shape, phase):
    p = phase % 1.0
    if shape == "square":
        return 1.0 if p < 0.5 else -1.0
    if shape == "triangle":
        return 4 * abs(p - 0.5) - 1
    if shape == "noise":
        return random.uniform(-1, 1)
    return math.sin(2 * math.pi * p)


def _tone(f0, dur, shape="square", vol=0.4, f1=None):
    n = int(_rate * dur)
    f1 = f0 if f1 is None else f1
    out = array.array("h")
    phase = 0.0
    for i in range(n):
        frac = i / n
        phase += (f0 + (f1 - f0) * frac) / _rate
        env = (1 - frac) ** 1.5
        if i < 80:
            env *= i / 80
        out.append(int(_wave(shape, phase) * env * vol * 32767))
    return out


def _seq(*parts):
    out = array.array("h")
    for part in parts:
        out.extend(part)
    return out


def _mix(a, b):
    n = max(len(a), len(b))
    out = array.array("h")
    for i in range(n):
        v = (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        out.append(max(-32767, min(32767, v)))
        return out


RECIPES = {
    "jump": lambda: _tone(330, 0.09, "square", 0.22, 520),
    "boing": lambda: _tone(200, 0.24, "triangle", 0.5, 760),
    "stomp": lambda: _mix(
        _tone(500, 0.12, "sqare", 0.3, 150), _tone(0, 0.07, "noise", 0.25)
    ),
    "pickup": lambda: _seq(
        _tone(440, 0.06, "square", 0.25),
        _tone(660, 0.06, "square", 0.25),
        _tone(880, 0.10, "square", 0.25),
    ),
    "hit": lambda: _mix(
        _tone(0, 0.25, "noise", 0.35), _tone(300, 0.25, "square", 0.3, 70)
    ),
    "fall": lambda: _tone(600, 0.55, "triangle", 0.4, 90),
    "crack": lambda: _tone(0, 0.12, "noise", 0.3),
    "bat": lambda: _tone(1500, 0.14, "square", 0.16, 900),
    "zone": lambda: _seq(
        _tone(523, 0.11, "triangle", 0.4),
        _tone(659, 0.11, "triangle", 0.4),
        _tone(784, 0.18, "triangle", 0.4),
    ),
    "win": lambda: _seq(
        _tone(523, 0.14, "triangle", 0.45),
        _tone(659, 0.14, "triangle", 0.45),
        _tone(784, 0.14, "triangle", 0.45),
        _tone(1047, 0.40, "triangle", 0.45),
    ),
    "move": lambda: _tone(500, 0.04, "square", 0.18),
    "select": lambda: _tone(750, 0.07, "square", 0.22),
}
for _n in range(2, 8):
    RECIPES[f"combo{_n}"] = lambda n=_n: _seq(
        _tone(520 * 1.12**n, 0.05, "triangle", 0.35),
        _tone(780 * 1.12**n, 0.09, "triangle", 0.35),
    )


def _make(mono):
    data = array.array("h")
    for s in mono:
        data.extend([s] * _channels)
    return pygame.mixer.Sound(buffer=data.tobytes())


def _get(name):
    if name in _cache:
        return _cache[name]
    snd = None
    for ext in (".wav", ".ogg"):
        path = os.path.join(SOUND_DIR, name + ext)
        if os.path.exists(path):
            try:
                snd = pygame.mixer.Sound(path)
            except pygame.error:
                snd = None
            break
    if snd is None and _synth_ok and name in RECIPES:
        try:
            snd = _make(RECIPES[name]())
        except (pygame.error, TypeError, ValueError):
            snd = None
    _cache[name] = snd
    return snd


def play(name, vol=1.0):
    if not _ready or _muted:
        return
    snd = _get(name)
    if snd:
        snd.set_volume(min(1.0, SFX_VOLUME * vol))
        snd.play()


def play_combo(n):
    play(f"combo{max(2,min(n,7))}")


def music_play():
    if not _ready:
        return
    for ext in (".ogg", ".mp3", ".wav"):
        path = os.path.join(SOUND_DIR, "music" + ext)
        if os.path.exists(path):
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.set_volume(0 if _muted else MUSIC_VOLUME)
                pygame.mixer.music.play(-1)
            except pygame.error:
                pass
            return


def music_pause():
    if _ready:
        pygame.mixer.music.pause()


def music_unpause():
    if _ready:
        pygame.mixer.music.unpause()


def music_stop():
    if _ready:
        pygame.mixer.music.stop()


def toggle_mute():
    global _muted
    _muted = not _muted
    if _ready:
        pygame.mixer.music.set_volume(0 if _muted else MUSIC_VOLUME)
    return _muted
