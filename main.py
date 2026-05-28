import pygame
import random
import math
import array as arr

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

WIDTH, HEIGHT = 800, 400
GROUND_Y = 320
GROUND_LINE_Y = 380
GRAVITY = 0.8
JUMP_FORCE = -15
DASH_W = 40
DASH_GAP = 30
OBSTACLE_MIN_INTERVAL = 60
OBSTACLE_MAX_INTERVAL = 120
SAMPLE_RATE = 44100

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Horse Runner 🐴")
clock = pygame.time.Clock()

# ── Icône de la fenêtre ──────────────────────────────────────
icon = pygame.Surface((32, 32), pygame.SRCALPHA)
pygame.draw.rect(icon, (139, 69, 19), (4,  14, 18,  9))   # corps
pygame.draw.rect(icon, (139, 69, 19), (17,  8,  6,  9))   # cou
pygame.draw.rect(icon, (139, 69, 19), (20,  4,  9,  7))   # tête
pygame.draw.rect(icon, (101, 50, 14), (15,  5,  6,  4))   # crinière
pygame.draw.rect(icon, (101, 50, 14), (1,  12,  4, 10))   # queue
for lx in [6, 11, 17, 22]:
    pygame.draw.rect(icon, (101, 50, 14), (lx, 23, 3, 8))  # pattes
pygame.display.set_icon(icon)

font_big   = pygame.font.SysFont(None, 64)
font_med   = pygame.font.SysFont(None, 36)
font_small = pygame.font.SysFont(None, 28)


# ── Génération de la musique ─────────────────────────────────
FREQ = {
    'C4': 261.63, 'E4': 329.63, 'G4': 392.00,
    'A4': 440.00, 'C5': 523.25, 'E5': 659.25,
}
MELODY = [
    ('G4', 0.12), ('G4', 0.12), ('C5', 0.12), ('E5', 0.24),
    ('C5', 0.12), ('A4', 0.12), ('G4', 0.12), ('E4', 0.24),
    ('G4', 0.12), ('A4', 0.12), ('C5', 0.12), ('E5', 0.24),
    ('C5', 0.12), ('G4', 0.12), ('E4', 0.12), ('C4', 0.36),
]
GAMEOVER_MELODY = [
    ('E5', 0.18), ('C5', 0.18), ('A4', 0.18),
    ('G4', 0.18), ('E4', 0.18), ('C4', 0.45),
]

def build_music_loop(melody, volume=0.20):
    total_samples = int(SAMPLE_RATE * sum(d for _, d in melody))
    buf = arr.array('h', [0] * (total_samples * 2))
    pos = 0
    for name, dur in melody:
        freq = FREQ[name]
        n = int(SAMPLE_RATE * dur)
        for i in range(n):
            t = i / SAMPLE_RATE
            decay = math.exp(-t * 12)
            val = int((math.sin(2 * math.pi * freq * t) * 0.7 +
                       math.sin(2 * math.pi * freq * 2 * t) * 0.3) * decay * volume * 32767)
            idx = (pos + i) * 2
            if idx + 1 < len(buf):
                buf[idx]     = max(-32768, min(32767, val))
                buf[idx + 1] = max(-32768, min(32767, val))
        pos += n
    return pygame.mixer.Sound(buffer=buf)

music         = build_music_loop(MELODY)
gameover_sound = build_music_loop(GAMEOVER_MELODY, volume=0.30)
music_ch      = pygame.mixer.Channel(0)
gameover_ch   = pygame.mixer.Channel(1)
music_ch.play(music, loops=-1)


# ── Décor : nuages roses et mouches ─────────────────────────
def make_cloud():
    return {
        "x":    float(WIDTH + random.randint(0, 200)),
        "y":    random.randint(20, 140),
        "size": random.randint(28, 55),
    }

def make_fly():
    return {
        "x":     float(WIDTH + random.randint(0, 300)),
        "y":     float(random.randint(50, 220)),
        "speed": random.uniform(1.5, 3.5),
        "vy":    random.uniform(-0.4, 0.4),
        "buzz":  random.uniform(0, math.pi * 2),  # phase d'oscillation
    }

clouds = [{"x": float(random.randint(0, WIDTH)),
           "y": random.randint(20, 140),
           "size": random.randint(28, 55)} for _ in range(5)]
flies  = [make_fly() for _ in range(6)]
# Disperse flies au départ sur tout l'écran
for f in flies:
    f["x"] = float(random.randint(0, WIDTH))

PINK       = (255, 182, 203)
PINK_DARK  = (240, 150, 170)
FLY_COLOR  = (20,  20,  20)
WING_COLOR = (80,  80, 110)

def draw_cloud(surface, x, y, size):
    pygame.draw.ellipse(surface, PINK,      (int(x),          y,          size * 2, size))
    pygame.draw.ellipse(surface, PINK,      (int(x) + size//2, y - size//3, size,    int(size * 0.8)))
    pygame.draw.ellipse(surface, PINK_DARK, (int(x) + size//4, y + size//2, size,    size // 3))

def draw_fly(surface, x, y):
    ix, iy = int(x), int(y)
    pygame.draw.circle(surface, FLY_COLOR,  (ix, iy), 4)
    pygame.draw.ellipse(surface, WING_COLOR, (ix - 8, iy - 4, 6, 3))
    pygame.draw.ellipse(surface, WING_COLOR, (ix + 2, iy - 4, 6, 3))


# ── Cheval ───────────────────────────────────────────────────
def draw_horse(surface, x, y, frame, jumping):
    brown      = (139, 69, 19)
    dark_brown = (101, 50, 14)
    pygame.draw.rect(surface, brown,      (x +  5, y + 18, 44, 24))
    pygame.draw.rect(surface, brown,      (x + 38, y +  8, 12, 18))
    pygame.draw.rect(surface, brown,      (x + 44, y +  2, 16, 14))
    pygame.draw.rect(surface, (0, 0, 0), (x + 56, y +  5,  3,  3))
    pygame.draw.rect(surface, dark_brown, (x + 58, y + 10,  3,  2))
    pygame.draw.rect(surface, dark_brown, (x + 36, y +  4, 10,  8))
    pygame.draw.rect(surface, dark_brown, (x +  2, y + 14,  6, 18))
    leg_top = y + 42
    if jumping:
        for ox in [10, 20, 34, 44]:
            pygame.draw.line(surface, dark_brown,
                             (x + ox, leg_top - 6), (x + ox + 4, leg_top + 4), 6)
    elif frame == 0:
        for ox, lean in [(10, 4), (20, -4), (34, -4), (44, 4)]:
            pygame.draw.line(surface, dark_brown,
                             (x + ox, leg_top), (x + ox + lean, leg_top + 18), 6)
    else:
        for ox, lean in [(10, -4), (20, 4), (34, 4), (44, -4)]:
            pygame.draw.line(surface, dark_brown,
                             (x + ox, leg_top), (x + ox + lean, leg_top + 18), 6)


# ── État du jeu ──────────────────────────────────────────────
def reset_game():
    return {
        "horse_y":          float(GROUND_Y),
        "vel_y":            0.0,
        "on_ground":        True,
        "obstacles":        [],
        "obstacle_timer":   0,
        "next_obstacle_in": random.randint(OBSTACLE_MIN_INTERVAL, OBSTACLE_MAX_INTERVAL),
        "score":            0,
        "speed":            6,
        "ground_offset":    0,
        "anim_frame":       0,
        "anim_timer":       0,
    }


horse_x = 100
state   = "start"

SCORE_FILE = "best_score.txt"
try:
    with open(SCORE_FILE) as f:
        best_score = int(f.read().strip())
except (FileNotFoundError, ValueError):
    best_score = 0
g          = reset_game()
tick       = 0

running = True
while running:
    clock.tick(60)
    tick += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if state == "start":
                state = "playing"
            elif state == "playing":
                if event.key in (pygame.K_SPACE, pygame.K_UP) and g["on_ground"]:
                    g["vel_y"]     = JUMP_FORCE
                    g["on_ground"] = False
            elif state == "gameover":
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    g     = reset_game()
                    state = "playing"
                    music_ch.play(music, loops=-1)

    # ── Mise à jour décor (tous états) ──────────────────────
    for cloud in clouds:
        cloud["x"] -= 0.8
    clouds[:] = [c for c in clouds if c["x"] + c["size"] * 2 > 0]
    while len(clouds) < 5:
        clouds.append(make_cloud())

    for fly in flies:
        fly["x"]    -= fly["speed"]
        fly["buzz"] += 0.15
        fly["y"]    += math.sin(fly["buzz"]) * 0.8
    flies[:] = [f for f in flies if f["x"] > -10]
    while len(flies) < 6:
        flies.append(make_fly())

    # ── Mise à jour jeu ──────────────────────────────────────
    if state == "playing":
        g["score"] += 1
        g["speed"]  = 6 + g["score"] // 200

        g["anim_timer"] += 1
        if g["on_ground"] and g["anim_timer"] >= 8:
            g["anim_frame"] = 1 - g["anim_frame"]
            g["anim_timer"] = 0

        g["vel_y"]   += GRAVITY
        g["horse_y"] += g["vel_y"]
        if g["horse_y"] >= GROUND_Y:
            g["horse_y"]   = float(GROUND_Y)
            g["vel_y"]     = 0.0
            g["on_ground"] = True

        g["ground_offset"] = (g["ground_offset"] - g["speed"]) % (DASH_W + DASH_GAP)

        g["obstacle_timer"] += 1
        if g["obstacle_timer"] >= g["next_obstacle_in"]:
            g["obstacles"].append({
                "x": WIDTH,
                "w": random.randint(20, 40),
                "h": random.randint(40, 80),
            })
            g["obstacle_timer"]   = 0
            g["next_obstacle_in"] = random.randint(OBSTACLE_MIN_INTERVAL, OBSTACLE_MAX_INTERVAL)

        for obs in g["obstacles"]:
            obs["x"] -= g["speed"]
        g["obstacles"] = [o for o in g["obstacles"] if o["x"] + o["w"] > 0]

        horse_rect = pygame.Rect(horse_x + 5, int(g["horse_y"]) + 18, 44, 24)
        for obs in g["obstacles"]:
            obs_rect = pygame.Rect(obs["x"], GROUND_LINE_Y - obs["h"], obs["w"], obs["h"])
            if horse_rect.colliderect(obs_rect):
                if g["score"] > best_score:
                    best_score = g["score"]
                    with open(SCORE_FILE, "w") as f:
                        f.write(str(best_score))
                state = "gameover"
                music_ch.stop()
                gameover_ch.play(gameover_sound)
                break

    # ── Dessin ───────────────────────────────────────────────
    screen.fill((220, 235, 255))   # ciel bleu clair

    # Nuages roses
    for c in clouds:
        draw_cloud(screen, c["x"], c["y"], c["size"])

    # Mouches
    for f in flies:
        draw_fly(screen, f["x"], f["y"])

    # Sol
    pygame.draw.line(screen, (0, 0, 0), (0, GROUND_LINE_Y), (WIDTH, GROUND_LINE_Y), 2)
    dx = g["ground_offset"] - (DASH_W + DASH_GAP)
    while dx < WIDTH:
        pygame.draw.rect(screen, (140, 120, 80), (dx, GROUND_LINE_Y + 4, DASH_W, 4))
        dx += DASH_W + DASH_GAP

    # Obstacles
    for obs in g["obstacles"]:
        pygame.draw.rect(screen, (200, 50, 50),
                         (obs["x"], GROUND_LINE_Y - obs["h"], obs["w"], obs["h"]))

    # Cheval
    draw_horse(screen, horse_x, int(g["horse_y"]), g["anim_frame"], not g["on_ground"])

    # Score en jeu
    if state == "playing":
        screen.blit(font_med.render(f"Score : {g['score']}", True, (50, 50, 50)),
                    (WIDTH - 200, 20))
        screen.blit(font_small.render(f"Meilleur : {best_score}", True, (100, 80, 60)),
                    (WIDTH - 200, 56))

    # Écran démarrage
    if state == "start":
        draw_horse(screen, WIDTH // 2 - 30, 230, 0, False)
        screen.blit(font_big.render("HORSE RUNNER", True, (80, 40, 0)),
                    (WIDTH // 2 - 190, 110))
        screen.blit(font_med.render("Appuie sur une touche pour commencer",
                                    True, (80, 60, 40)),
                    (WIDTH // 2 - 270, 185))

    # Écran game over
    if state == "gameover":
        screen.blit(font_big.render("GAME OVER", True, (200, 50, 50)),
                    (WIDTH // 2 - 160, 100))
        screen.blit(font_med.render(f"Score : {g['score']}", True, (50, 50, 50)),
                    (WIDTH // 2 - 80, 180))
        screen.blit(font_med.render(f"Meilleur : {best_score}", True, (80, 40, 0)),
                    (WIDTH // 2 - 100, 220))
        screen.blit(font_small.render("Espace ou Entrée pour rejouer",
                                      True, (80, 60, 40)),
                    (WIDTH // 2 - 170, 280))

    pygame.display.update()

pygame.quit()
