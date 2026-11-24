import json
import os
import sys
import pygame
from settings import *

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
window = pygame.display.set_mode((W * SCALE, H * SCALE))
pygame.display.set_caption(TITLE)
canvas = pygame.Surface((W, H))
clock = pygame.time.Clock()
ft = pygame.font.Font(None, 20)
big_ft = pygame.font.Font(None, 40)

from world import World
import sound

sound.init()

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), HIGHSCORE_FILE)
WHITE = (255, 255, 255)
GOLD = (255, 230, 90)
GREY = (200, 200, 200)
PAUSE_MENU = ["Resume", "Restart", "Quit"]


def load_best():
    try:
        with open(SAVE_PATH) as f:
            return int(json.load(f).get("best", 0))
    except (OSError, ValueError, AttributeError):
        return 0


def save_best(best):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump({"best": best}, f)
    except OSError:
        pass


def txt(surf, msg, y, f=ft, color=WHITE):
    img = f.render(msg, False, color)
    surf.blit(img, (W // 2 - img.get_width() // 2, y))


def dim(surf, alpha=150):
    shade = pygame.Surface((W, H), pygame.SRCALPHA)
    shade.fill((0, 0, 0, alpha))
    surf.blit(shade, (0, 0))


def quit_game(world):
    save_best(world.best)
    pygame.quit()
    sys.exit()


def restart(world):
    best = world.best
    world.reset()
    world.best = best


def draw_hud(surf, world):
    surf.blit(ft.render(f"Score: {world.score}", False, WHITE), (6, 6))
    surf.blit(ft.render(f"Best: {world.best}", False, WHITE), (6, 20))
    surf.blit(ft.render(f"{world.height}m  {world.zone.name}", False, WHITE), (6, 34))
    if world.player.jetpack > 0:
        fuel = int(60 * world.player.jetpack / JETPACK_FRAMES)
        pygame.draw.rect(surf, (60, 60, 60), (6, 48, 60, 6))
        pygame.draw.rect(surf, (255, 160, 40), (6, 48, fuel, 6))
    if world.combo >= 2:
        img = ft.render(f"COMBO x{world.combo}", False, GOLD)
        surf.blit(img, (W - img.get_width() - 6, 6))


def draw_notice(surf, world):
    if world.notice_timer > 0:
        txt(surf, world.notice, 70, big_ft, GOLD)
        txt(surf, world.notice_sub, 98, ft, WHITE)


def draw_pause(surf, menu_i):
    dim(surf)
    txt(surf, "PAUSED", 90, big_ft)
    for i, item in enumerate(PAUSE_MENU):
        sel = i == menu_i
        y = 150 + i * 20
        txt(surf, item, y, ft, GOLD if sel else WHITE)
        if sel:
            w_ = ft.render(item, False, WHITE).get_width()
            surf.blit(ft.render(">", False, GOLD), (W // 2 - w_ // 2 - 14, y))
    txt(surf, "W/S + Enter   Esc = resume", H - 30, ft, GREY)


def draw_game_over(surf, world, best_before):
    dim(surf, 170)
    if world.death_cause == "fell":
        txt(surf, "You fell!", 80, big_ft)
    else:
        txt(surf, "Owh!", 80, big_ft)
        txt(surf, world.death_cause, 110, ft, (220, 160, 160))
    txt(surf, f"Score: {world.score}", 145)
    txt(surf, f"Height: {world.height}m    Zone: {world.zone.name}", 163)
    if world.best > best_before:
        txt(surf, "NEW BEST!", 195, ft, GOLD)
    else:
        txt(surf, f"Best: {world.best}", 195)
    txt(surf, "R = try again    Esc = quit", H - 30, ft, GREY)


def draw_win(surf, world, best_before):
    dim(surf, 150)
    txt(surf, "THE PEAK!", 70, big_ft, GOLD)
    txt(surf, "You made it to the top! YAY!", 105)
    secs = world.tick // FPS
    txt(surf, f"Score: {world.score}", 140)
    txt(surf, f"Time: {secs//60}:{secs%60:02d}", 158)
    if world.best > best_before:
        txt(surf, "NEW BEST!", 180, ft, GOLD)
    txt(surf, "C = keep climbing (endless)", 235, ft, WHITE)
    txt(surf, "R = new run    Esc = quit", 255, ft, GREY)


def main():
    world = World()
    world.best = load_best()
    best_before = world.best
    state = "title"
    menu_i = 0
    save = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game(world)
            if event.type != pygame.KEYDOWN:
                continue
            key = event.key
            if key == pygame.K_m:
                sound.toggle_mute()
                continue
            if state == "title":
                if key in (pygame.K_SPACE, pygame.K_RETURN):
                    state = "play"
                    sound.play("select")
                    sound.music_play()
                elif key == pygame.K_ESCAPE:
                    quit_game(world)
            elif state == "play":
                if key == pygame.K_r:
                    restart(world)
                    save, best_before = False, world.best
                    sound.music_play()
                elif key in (pygame.K_ESCAPE, pygame.K_p):
                    if world.dead:
                        quit_game(world)
                    else:
                        state, menu_i = "paused", 0
                        sound.music_pause()
                        sound.play("select")
            elif state == "paused":
                if key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "play"
                    sound.music_unpause()
                elif key in (pygame.K_UP, pygame.K_w):
                    menu_i = (menu_i - 1) % len(PAUSE_MENU)
                    sound.play("move")
                elif key in (pygame.K_DOWN, pygame.K_s):
                    menu_i = (menu_i + 1) % len(PAUSE_MENU)
                    sound.play("move")
                elif key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = PAUSE_MENU[menu_i]
                    sound.play("select")
                    if choice == "Resume":
                        state = "play"
                        sound.music_unpause()
                    elif choice == "Restart":
                        restart(world)
                        save, best_before = False, world.best
                        state = "play"
                        sound.music_play()
                    else:
                        quit_game(world)
            elif state == "won":
                if key == pygame.K_c:
                    world.endless = True
                    state = "play"
                    sound.music_play()
                elif key == pygame.K_r:
                    restart(world)
                    save, best_before = False, world.best
                    state = "play"
                    sound.music_play()
                elif key == pygame.K_ESCAPE:
                    quit_game(world)
        if state == "play":
            world.update(pygame.key.get_pressed())
            if world.won and not world.endless:
                state = "won"
                save_best(world.best)
                sound.music_stop()
                sound.play("win")
            if world.dead and not save:
                save_best(world.best)
                save = True
                sound.music_stop()
        world.draw(canvas)
        if state == "title":
            txt(canvas, "PEAK", 100, big_ft)
            txt(canvas, "Press SPACE to climb", 150)
            txt(canvas, f"Best: {world.best}", 175)
            txt(canvas, "A/D or arrows = move   P = pause", H - 30, ft, GREY)
            txt(canvas, "M = mute sound", H - 16, ft, GREY)
        else:
            draw_hud(canvas, world)
            if state == "play" and not world.dead:
                draw_notice(canvas, world)
            if state == "paused":
                draw_pause(canvas, menu_i)
            elif state == "won":
                draw_win(canvas, world, best_before)
            elif world.dead:
                draw_game_over(canvas, world, best_before)
        ox, oy = (0.0, 0.0) if state == "paused" else world.shake.update()
        scale = pygame.transform.scale(canvas, window.get_size())
        window.fill((0, 0, 0))
        window.blit(scale, (int(ox * SCALE), int(oy * SCALE)))
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
