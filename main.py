import json
import os
import sys
import pygame
from settings import * 
pygame.init()
window = pygame.display.set_mode((W*SCALE,H*SCALE))
pygame.display.set_caption(TITLE)
canvas = pygame.Surface((W,H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 20)
big_ft = pygame.font.Font(None, 40)

from world import World

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), HIGHSCORE_FILE)

def load_best():
    try:
        with open(SAVE_PATH) as f:
            return int(json.load(f). get("best", 0))
    except (OSError, ValueError,AttributeError):
        return 0
def save_best(best):
    try:
        with open(SAVE_PATH,"w") as f:
            json.dump({"best": best},f)
    except OSError:
        pass
def txt(surf,msg,y,f=ft,color=(255,255,255)):
    img = f.render(msg,False,color)
    surf.blit(img,(W//2-img.get_width()//2,y))
def main():
    world = World()
    world.best = load_best()
    state = "title"
    banner = 0
    saved = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_best(world.best)
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_best(world.best)
                    pygame.quit()
                    sys.exit()
                if state == "title" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    state = "play"
                if event.key == pygame.K_r and state == "play":
                    best = world.best
                    world.reset()
                    world.best = best
                    banner, saved = 0, False
        if state == "play":
            was_peak = world.reach_peak
            world.update(pygame.key.get_pressed())
            if world.reach_peak and not was_peak:
                banner = FPS * 4
            if world.dead and not saved:
                save_best(world.best)
                saved = True
        world.draw(canvas)
        if state == "title":
            txt(canvas, "PEAK", 100, big_ft)
            txt(canvas, "Press SPACE to climb", 150)
            txt(canvas, f"Best: {world.best}", 175)
        else:
            canvas.blit(ft.render(f"Height: {world.height}", False, (255,255,255)), (6,6))
            canvas.blit(ft.render(f"Best: {world.best}", False, (255,255,255)), (6,20))
            canvas.blit(ft.render(world.zone.name, False, (255,255,255)), (6,34))
            if banner > 0:
                banner -= 1
                txt(canvas, "YOU REACHED PEAK WOW AMAZING!", 80, ft, (255,230,90))
            if world.dead:
                txt(canvas, "You fell!", H//2-20, big_ft)
                txt(canvas, "Press R to try again", H//2+10)

        ox, oy = world.shake.update()
        scale = pygame.transform.scale(canvas, window.get_size())
        window.fill((0,0,0))
        window.blit(scale, (int(ox*SCALE), int(oy*SCALE)))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()