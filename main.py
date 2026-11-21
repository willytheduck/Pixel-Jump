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
WHITE = (255,255,255)
GOLD = (255,230,90)
PAUSE_MENU = ["Resume", "Restart", "Quit"]

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
def txt(surf,msg,y,f=ft,color=WHITE):
    img = f.render(msg,False,color)
    surf.blit(img,(W//2-img.get_width()//2,y))
def dim(surf, alpha=150):
    shade = pygame.Surface((W,H), pygame.SRCALPHA)
    shade.fill((0,0,0,alpha))
    surf.blit(shade,(0,0))
def quit_game(world):
    save_best(world.best)
    pygame.quit()
    sys.exit()
def restart(world):
    best = world.best
    world.reset()
    world.best = best
def draw_pause(surf, menu_i):
    dim(surf)
    txt(surf, "PAUSED", 90, big_ft)
    for i, item in enumerate(PAUSE_MENU):
        sel = (i == menu_i)
        y = 150+i*20
        txt(surf,item,y,ft,GOLD if sel else WHITE)
        if sel:
            w_ = ft.render(item,False,WHITE).get_width()
            surf.blit(ft.render(">", False, GOLD), (W//2 - w_//2 - 14, y))
    txt(surf,"W/S + Enter   Esc = resume", H-30, ft, (200,200,200))
def draw_game_over(surf,world,best_before):
    dim(surf,170)
    if world.death_cause == "fell":
        txt(surf, "You fell!", 80, big_ft)
    else:
        txt(surf, "Owh!", 80, big_ft)
        txt(surf, f"Hit by a {world.death_cause}", 110, ft, (220,160,160))
    txt(surf, f"Height: {world.height}", 150)
    txt(surf, f"Zone: {world.zone.name}", 168)
    if world.best > best_before:
        txt(surf,"NEW BEST!", 195, ft, GOLD)
    else:
        txt(surf, f"Best: {world.best}", 195)
    txt(surf, "R = try again    Esc = quit", H-30, ft, (200,200,200))

def main():
    world =World()
    world.best=load_best()
    best_before = world.best
    state = "title"
    menu_i =0
    banner=0
    save = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game(world)
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key
            if state == "title":
                if key in (pygame.K_SPACE, pygame.K_RETURN):
                    state = "play"
                elif key == pygame.K_ESCAPE:
                    quit_game(world)
            elif state == "play":
                if key == pygame.K_r:
                    restart(world)
                    banner, save, best_before=0,False,world.best
                elif key in (pygame.K_ESCAPE, pygame.K_p):
                    if world.dead:
                        quit_game(world)
                    else:
                        state, menu_i = "paused", 0
            elif state == "paused":
                if key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "play"
                elif key in (pygame.K_UP, pygame.K_w):
                    menu_i = (menu_i - 1) % len(PAUSE_MENU)
                elif key in (pygame.K_DOWN, pygame.K_s):
                    menu_i = (menu_i + 1) % len(PAUSE_MENU)
                elif key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = PAUSE_MENU[menu_i]
                    if choice == "Resume":
                        state = "play"
                    elif choice == "Restart":
                        restart(world)
                        banner, save, best_before = 0, False, world.best
                        state = "play"
                    else:
                        quit_game(world)
        if state == "play":
            was_peak = world.reach_peak
            world.update(pygame.key.get_pressed())
            if world.reach_peak and not was_peak:
                banner = FPS * 4
            if world.dead and not save:
                save_best(world.best)
                save = True
        world.draw(canvas)
        if state == "title":
            txt(canvas, "PEAK", 100, big_ft)
            txt(canvas, "Press SPACE to climb", 150)
            txt(canvas, f"Best: {world.best}", 175)
            txt(canvas, "A/D or arrows = move   P = pause", H-30, ft, (200,200,200))
        else:
            canvas.blit(ft.render(f"Height: {world.height}", False, WHITE), (6,6))
            canvas.blit(ft.render(f"Best: {world.best}", False, WHITE), (6,20))
            canvas.blit(ft.render(world.zone.name, False, WHITE), (6,34))
            if world.player.jetpack > 0:
                fuel = int(60*world.player.jetpack/JETPACK_FRAMES)
                pygame.draw.rect(canvas, (60,60,60), (6,48,60,6))
                pygame.draw.rect(canvas, (255,160,40), (6,48,fuel,6))
            if banner > 0 and state == "play":
                banner -= 1
                txt(canvas, "YOU REACHED PEAK HOLY COW!",80,ft,GOLD)
            if state == "paused":
                draw_pause(canvas, menu_i)
            elif world.dead:
                draw_game_over(canvas, world, best_before)
        ox,oy = (0.0,0.0) if state == "paused" else world.shake.update()
        scale= pygame.transform.scale(canvas, window.get_size())
        window.fill((0,0,0))
        window.blit(scale,(int(ox*SCALE), int(oy*SCALE)))
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()