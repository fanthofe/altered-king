#!/usr/bin/env python3
"""Génère les sprites pixel art du jeu (PNG) dans assets/sprites/.

Usage : python3 tools/gen_sprites.py
Chaque sprite est décrit soit par une grille de caractères (1 char = 1 pixel),
soit dessiné procéduralement (tuiles, buisson). Modifier puis relancer.
"""
import os
import struct
import sys
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "sprites")


def hex_rgba(code: str, alpha: int = 255):
    code = code.lstrip("#")
    return (int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16), alpha)


TRANSPARENT = (0, 0, 0, 0)


def write_png(rel_path: str, pixels) -> None:
    """pixels : liste de lignes de tuples RGBA."""
    height = len(pixels)
    width = len(pixels[0])
    raw = b"".join(
        b"\x00" + b"".join(struct.pack("4B", *px) for px in row) for row in pixels
    )

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path = os.path.join(OUT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)
    print(f"  {os.path.relpath(path, ROOT)}  ({width}x{height})")


def render(grid, legend):
    """Convertit une grille de caractères en pixels RGBA."""
    widths = {len(row) for row in grid}
    assert len(widths) == 1, f"largeurs incohérentes : {widths}"
    return [
        [legend.get(ch, TRANSPARENT) for ch in row]
        for row in grid
    ]


# --------------------------------------------------------------------------
# Le roi déchu (16x24) — corps d'esclave décharné, couronne d'or, yeux spectraux
# --------------------------------------------------------------------------
KING = {
    "G": hex_rgba("#c9a227"),  # couronne
    "S": hex_rgba("#d8c8a8"),  # peau blafarde
    "s": hex_rgba("#b09878"),  # peau ombrée
    "E": hex_rgba("#7fd8ea"),  # yeux spectraux
    "e": hex_rgba("#b8f0f0"),  # étincelle de magie
    "T": hex_rgba("#5a4a56"),  # haillons
    "t": hex_rgba("#453a44"),  # haillons ombrés
    "B": hex_rgba("#7a6448"),  # corde-ceinture
    "P": hex_rgba("#3a3038"),  # braies
}

KING_TOP = [
    "................",
    "................",
    "....G..G..G.....",
    "....GGGGGGG.....",
    "....SSSSSSS.....",
    "....SESSSES.....",
    "....SSSSSSS.....",
    ".....SSSSS......",
    ".....sSSSs......",
    "....TTTTTTT.....",
    "...TTTTTTTTT....",
    "...TtTTTTTtT....",
    "...TtTTTTTtT....",
    "...StTTTTTtS....",
    "....BBBBBBB.....",
    "....TTTTTTT.....",
    "....tTTTTTt.....",
]

KING_LEGS_IDLE = [
    "....PP...PP.....",
    "....PP...PP.....",
    "....PP...PP.....",
    "....PP...PP.....",
    "....ss...ss.....",
    "...SSS...SSS....",
    "...SSS...SSS....",
]

KING_LEGS_STRIDE = [
    "...PP.....PP....",
    "...PP.....PP....",
    "...PP.....PP....",
    "..PP.......PP...",
    "..ss.......ss...",
    ".SSS.......SSS..",
    ".SSS.......SSS..",
]

KING_CAST_TORSO = [
    "..e.........e...",
    "...S.TTTTT.S....",
    "...StTTTTTtS....",
    "....TTTTTTT.....",
    "....TTTTTTT.....",
    "....TTTTTTT.....",
]

KING_CAST_TORSO_ALT = [
    ".e...........e..",
    "...e.TTTTT.e....",
    "...StTTTTTtS....",
    "....TTTTTTT.....",
    "....TTTTTTT.....",
    "....TTTTTTT.....",
]

king_idle_0 = KING_TOP + KING_LEGS_IDLE
king_idle_1 = [row.replace("E", "s") for row in KING_TOP] + KING_LEGS_IDLE
king_walk_0 = KING_TOP + KING_LEGS_STRIDE
king_walk_1 = KING_TOP + KING_LEGS_IDLE
king_cast_0 = KING_TOP[:8] + KING_CAST_TORSO + KING_TOP[14:] + KING_LEGS_IDLE
king_cast_1 = KING_TOP[:8] + KING_CAST_TORSO_ALT + KING_TOP[14:] + KING_LEGS_IDLE

# --------------------------------------------------------------------------
# Le geôlier (16x24) — brute encapuchonnée de fer, tunique cramoisie, gourdin
# --------------------------------------------------------------------------
JAILER = {
    "M": hex_rgba("#8a8a9a"),  # capuche de fer
    "m": hex_rgba("#565664"),  # fer sombre / bottes
    "E": hex_rgba("#e8a04a"),  # fente du regard
    "R": hex_rgba("#7e2d34"),  # tunique cramoisie
    "r": hex_rgba("#571f24"),  # tunique ombrée / jambes
    "C": hex_rgba("#6b4a2f"),  # gourdin
    "c": hex_rgba("#493320"),  # gourdin ombré
}

JAILER_TOP = [
    "................",
    "................",
    "................",
    "................",
    "................",
    "....mmmmmm......",
    "...mMMMMMMm.....",
    "...mMEMMEMm.....",
    "...mMMMMMMm.Cc..",
    "....mmmmmm..Cc..",
    "...RRRRRRRR.Cc..",
    "..RRRRRRRRRRCc..",
    "..RrRRRRRRrRCc..",
    "..RrRRRRRRrRCc..",
    "..RrRRRRRRrR....",
    "..rRRRRRRRRr....",
    "...RRRRRRRR.....",
]

JAILER_LEGS_STRIDE = [
    "...rr.....rr....",
    "...rr.....rr....",
    "...rr.....rr....",
    "..mm.......mm...",
    "..mm.......mm...",
    ".mmm.......mmm..",
    ".mmm.......mmm..",
]

JAILER_LEGS_TOGETHER = [
    "....rr...rr.....",
    "....rr...rr.....",
    "....rr...rr.....",
    "....mm...mm.....",
    "....mm...mm.....",
    "...mmm...mmm....",
    "...mmm...mmm....",
]

jailer_walk_0 = JAILER_TOP + JAILER_LEGS_STRIDE
jailer_walk_1 = JAILER_TOP + JAILER_LEGS_TOGETHER

# --------------------------------------------------------------------------
# Torche murale (8x16), flamme animée sur 2 frames
# --------------------------------------------------------------------------
TORCH = {
    "Y": hex_rgba("#f6d35e"),  # coeur de flamme
    "O": hex_rgba("#e8862a"),  # flamme
    "c": hex_rgba("#4a3320"),  # manche
    "m": hex_rgba("#6a6a78"),  # anneau de fer
}

torch_0 = [
    "........",
    "...Y....",
    "..YYO...",
    "..OYO...",
    "..OYYO..",
    "...OO...",
    "...cc...",
    "...cc...",
    "...cc...",
    "...cc...",
    "..mmmm..",
    "...cc...",
    "...cc...",
    "........",
    "........",
    "........",
]

torch_1 = [
    "........",
    "....Y...",
    "...OYY..",
    "...OYO..",
    "..OYYO..",
    "...OO...",
    "...cc...",
    "...cc...",
    "...cc...",
    "...cc...",
    "..mmmm..",
    "...cc...",
    "...cc...",
    "........",
    "........",
    "........",
]

# --------------------------------------------------------------------------
# Buisson (28x24) — dessiné procéduralement
# --------------------------------------------------------------------------
def make_bush():
    w, h = 28, 24
    px = [[TRANSPARENT] * w for _ in range(h)]
    base = hex_rgba("#2c5636")
    shadow = hex_rgba("#1f4128")
    light = hex_rgba("#3d7a4a")
    berry = hex_rgba("#8a3550")

    def blob(cx, cy, r, col):
        for y in range(h):
            for x in range(w):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    px[y][x] = col

    blob(9, 15, 7, base)
    blob(19, 14, 8, base)
    blob(14, 9, 7, base)
    # Ombre portée sur le bas de la masse feuillue.
    for y in range(18, h):
        for x in range(w):
            if px[y][x] != TRANSPARENT:
                px[y][x] = shadow
    # Reflets sur le haut.
    for cx, cy, r in ((12, 6, 2), (6, 11, 2), (18, 8, 2)):
        for y in range(h):
            for x in range(w):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r and px[y][x] == base:
                    px[y][x] = light
    # Quelques baies.
    for bx, by in ((8, 13), (16, 16), (21, 11), (13, 12)):
        if px[by][bx] != TRANSPARENT:
            px[by][bx] = berry
    return px


# --------------------------------------------------------------------------
# Tuiles de pierre 16x16 (sol) et variante assombrie (fond), pilier 20x16
# --------------------------------------------------------------------------
def make_stone_tile(scale: float = 1.0):
    def shade(code):
        r, g, b, a = hex_rgba(code)
        return (int(r * scale), int(g * scale), int(b * scale), a)

    base = shade("#2e2a38")
    mortar = shade("#1d1928")
    top = shade("#453f54")
    speck = shade("#282436")

    w = h = 16
    px = [[base] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            row = 0 if y < 8 else 1
            # Joints horizontaux entre rangées de briques.
            if y in (7, 15):
                px[y][x] = mortar
                continue
            # Joints verticaux, décalés une rangée sur deux.
            joints = (7,) if row == 0 else (3, 11)
            if x in joints:
                px[y][x] = mortar
                continue
            # Arête éclairée en haut de chaque brique.
            if y in (0, 8):
                px[y][x] = top
            elif (x * 7 + y * 3) % 13 == 0:
                px[y][x] = speck
    return px


def make_pillar_tile():
    w, h = 20, 16
    base = hex_rgba("#262233")
    dark = hex_rgba("#1b1826")
    light = hex_rgba("#322c44")
    band = hex_rgba("#221e30")
    px = [[base] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            if x in (0, 1, 18, 19):
                px[y][x] = dark
            elif x in (2, 3):
                px[y][x] = light
            elif y in (7, 8):
                px[y][x] = band
    return px


# --------------------------------------------------------------------------
# Forêt — inspirée de assets/sprites/references/scene.jpg :
# clairière lumineuse, troncs massifs mousseux, canopée dense, brume verte.
# --------------------------------------------------------------------------
def _lerp_color(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(4))


def make_forest_gradient():
    """Fond vertical : canopée sombre en haut, brume verte vers le sol."""
    w, h = 8, 360
    stops = [
        (0, hex_rgba("#1a3028")),
        (140, hex_rgba("#33584a")),
        (280, hex_rgba("#4a7a5e")),
        (359, hex_rgba("#5e9268")),
    ]
    px = []
    for y in range(h):
        for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
            if y0 <= y <= y1:
                t = (y - y0) / max(y1 - y0, 1)
                px.append([_lerp_color(c0, c1, t)] * w)
                break
    return px


def make_far_trees():
    """Silhouettes d'arbres lointains dans la brume (tuile 192x360)."""
    w, h = 192, 360
    px = [[TRANSPARENT] * w for _ in range(h)]
    body = hex_rgba("#2b4a3f")
    edge = hex_rgba("#223b33")
    bush_far = hex_rgba("#1d332b")
    bush_near = hex_rgba("#244034")
    leaf = hex_rgba("#35594a")

    import math
    # Peu de troncs, épais et espacés : la brume doit respirer entre eux.
    for cx, half in ((34, 6), (128, 10)):
        for y in range(h):
            wob = int(2 * math.sin(y / 37.0 + cx))
            for x in range(cx - half + wob, cx + half + wob):
                if 0 <= x < w:
                    is_edge = x in (cx - half + wob, cx + half + wob - 1)
                    px[y][x] = edge if is_edge else body
    # Feuillage épars accroché aux troncs.
    for i in range(120):
        x = (i * 37 + 11) % w
        y = (i * 53 + 29) % 200
        if px[y][x] == body:
            px[y][x] = leaf
    # Sous-bois : masses arrondies qui dépassent de la prairie (sol à y=336).
    def blob(cx, cy, r, col):
        for y in range(max(cy - r, 0), min(cy + r + 1, h)):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    px[y][x % w] = col

    for i in range(8):
        blob((i * 27 + 9) % w, 334, 9 + (i * 5) % 6, bush_far)
    for i in range(6):
        blob((i * 37 + 22) % w, 338, 7 + (i * 3) % 4, bush_near)
    return px


def make_trunk():
    """Gros tronc d'arbre (48x240) : écorce striée, lierre et mousse."""
    w, h = 48, 240
    px = [[TRANSPARENT] * w for _ in range(h)]
    bark = hex_rgba("#6b4a34")
    bark_dark = hex_rgba("#4a3122")
    bark_light = hex_rgba("#7d5a40")
    moss = hex_rgba("#3f7a4a")
    moss_dark = hex_rgba("#2c5636")

    import math
    cx = w // 2
    for y in range(h):
        half = 13
        if y > 190:
            half = 13 + (y - 190) * 9 // 50  # évasement des racines
        wob = int(1.5 * math.sin(y / 23.0))
        x0, x1 = cx - half + wob, cx + half + wob
        for x in range(x0, x1):
            if not 0 <= x < w:
                continue
            if x <= x0 + 1:
                px[y][x] = bark_light  # lumière venant de la gauche
            elif x >= x1 - 2:
                px[y][x] = bark_dark
            else:
                rel = x - cx - wob
                ridge = rel in (-7, -2, 4, 9) and (y + rel * 3) % 9 < 6
                px[y][x] = bark_dark if ridge else bark

    def moss_blob(mx, my, r):
        for y in range(my - r, my + r + 1):
            for x in range(mx - r, mx + r + 1):
                if (x - mx) ** 2 + (y - my) ** 2 <= r * r \
                        and 0 <= x < w and 0 <= y < h \
                        and px[y][x] != TRANSPARENT:
                    px[y][x] = moss if (x + y) % 3 else moss_dark

    for mx, my, r in ((14, 30, 4), (32, 74, 4), (12, 122, 6),
                      (34, 168, 5), (16, 205, 7), (30, 228, 6)):
        moss_blob(mx, my, r)
    return px


def make_canopy():
    """Canopée (tuile 64x64) : masses de feuilles, bord inférieur irrégulier."""
    w, h = 64, 64
    px = [[TRANSPARENT] * w for _ in range(h)]
    base = hex_rgba("#1e3b2a")
    mid = hex_rgba("#2c5636")
    light = hex_rgba("#3d7a4a")
    sparkle = hex_rgba("#79c470")

    def blob(cx, cy, r, col):
        for y in range(max(cy - r, 0), min(cy + r + 1, h)):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    px[y][x % w] = col  # repli horizontal : tuile sans couture

    for y in range(26):
        for x in range(w):
            px[y][x] = base
    for i in range(9):
        blob((i * 23 + 7) % w, 20 + (i * 11) % 22, 12 + (i * 7) % 7, base)
    for i in range(10):
        blob((i * 19 + 3) % w, 12 + (i * 13) % 20, 6 + (i * 5) % 5, mid)
    for i in range(8):
        blob((i * 29 + 15) % w, 6 + (i * 7) % 14, 3 + (i * 3) % 3, light)
    for i in range(26):
        x, y = (i * 41 + 5) % w, (i * 17 + 3) % 30
        if px[y][x] != TRANSPARENT:
            px[y][x] = sparkle
    return px


def make_grass_tile():
    """Sol de clairière (16x24) : herbe lumineuse fleurie sur terre sombre."""
    w, h = 16, 24
    top = hex_rgba("#7fb35c")
    top_light = hex_rgba("#a8d97a")
    grass = hex_rgba("#5c8f46")
    grass_dark = hex_rgba("#4a6b38")
    dirt = hex_rgba("#4a3a2c")
    dirt_dark = hex_rgba("#3a2d20")
    stone = hex_rgba("#5c5a4e")
    flower_w = hex_rgba("#e8e8d0")
    flower_y = hex_rgba("#e8d060")

    px = [[dirt] * w for _ in range(h)]
    for x in range(w):
        # Prairie profonde et lumineuse : 10 rangs d'herbe avant la terre.
        for y in range(0, 3):
            px[y][x] = top_light if (x * 5 + y * 3 + 1) % 4 == 0 else top
        for y in range(3, 9):
            px[y][x] = grass_dark if (x * 7 + y * 13) % 11 == 0 else grass
        px[9][x] = grass_dark
        for y in range(10, h):
            if (x * 7 + y * 13) % 23 == 0:
                px[y][x] = dirt_dark
            elif (x * 11 + y * 5) % 37 == 0:
                px[y][x] = stone
    # Quelques fleurs dans l'herbe.
    for fx, fy, col in ((3, 1, flower_w), (9, 3, flower_y), (13, 2, flower_w),
                        (6, 5, flower_y)):
        px[fy][fx] = col
    return px


def make_log_tile():
    """Branche-plateforme (16x12) : bois strié coiffé de mousse."""
    w, h = 16, 12
    moss = hex_rgba("#3d7a4a")
    moss_dark = hex_rgba("#2c5636")
    wood = hex_rgba("#6b4a34")
    wood_dark = hex_rgba("#4a3122")
    px = [[wood] * w for _ in range(h)]
    for x in range(w):
        px[0][x] = moss
        px[1][x] = moss if (x * 3 + 1) % 5 else moss_dark
        px[2][x] = moss_dark if (x * 5 + 2) % 7 == 0 else moss
        for y in range(3, h):
            if y in (5, 8) and (x + y) % 9 < 6:
                px[y][x] = wood_dark
        px[h - 1][x] = wood_dark
    return px


def make_rock(w: int, h: int):
    """Rocher arrondi gris-vert, éclairé par le haut."""
    body = hex_rgba("#7d8577")
    light = hex_rgba("#a0a894")
    shadow = hex_rgba("#55604f")
    px = [[TRANSPARENT] * w for _ in range(h)]
    cx, cy = (w - 1) / 2, (h - 1) / 2
    for y in range(h):
        for x in range(w):
            if ((x - cx) / cx) ** 2 + ((y - cy) / cy) ** 2 <= 1.0:
                if y < h * 0.35 and x < w * 0.7:
                    px[y][x] = light
                elif y > h * 0.7:
                    px[y][x] = shadow
                else:
                    px[y][x] = body
    return px


def make_tuft(with_flower: bool):
    """Touffe d'herbe (10x8), avec ou sans fleur."""
    w, h = 10, 8
    px = [[TRANSPARENT] * w for _ in range(h)]
    greens = [hex_rgba("#5c8f46"), hex_rgba("#7fb35c"), hex_rgba("#a8d97a")]
    heights = {1: 4, 3: 6, 5: 5, 7: 3, 8: 5}
    for x, blade_h in heights.items():
        for i in range(blade_h):
            px[h - 1 - i][x] = greens[(x + i) % 3]
    if with_flower:
        px[h - 7][3] = hex_rgba("#e8d060")
        px[h - 6][7] = hex_rgba("#e8e8d0")
    return px


def make_mote(bright: bool):
    """Luciole (4x4) : point de lumière flottant."""
    px = [[TRANSPARENT] * 4 for _ in range(4)]
    core = hex_rgba("#d8f0b0")
    halo = hex_rgba("#d8f0b0", 110 if bright else 50)
    if bright:
        px[1][1] = px[1][2] = px[2][1] = px[2][2] = core
        px[0][1] = px[1][0] = px[3][2] = px[2][3] = halo
    else:
        px[1][1] = core
        px[2][2] = halo
    return px


def main() -> None:
    print("Génération des sprites…")
    write_png("player/idle_0.png", render(king_idle_0, KING))
    write_png("player/idle_1.png", render(king_idle_1, KING))
    write_png("player/walk_0.png", render(king_walk_0, KING))
    write_png("player/walk_1.png", render(king_walk_1, KING))
    write_png("player/cast_0.png", render(king_cast_0, KING))
    write_png("player/cast_1.png", render(king_cast_1, KING))
    write_png("enemies/jailer_walk_0.png", render(jailer_walk_0, JAILER))
    write_png("enemies/jailer_walk_1.png", render(jailer_walk_1, JAILER))
    write_png("props/torch_0.png", render(torch_0, TORCH))
    write_png("props/torch_1.png", render(torch_1, TORCH))
    write_png("props/bush.png", make_bush())
    write_png("tiles/floor.png", make_stone_tile(1.0))
    write_png("tiles/wall.png", make_stone_tile(0.62))
    write_png("tiles/pillar.png", make_pillar_tile())
    write_png("forest/gradient.png", make_forest_gradient())
    write_png("forest/far_trees.png", make_far_trees())
    write_png("forest/trunk.png", make_trunk())
    write_png("forest/canopy.png", make_canopy())
    write_png("forest/grass.png", make_grass_tile())
    write_png("forest/log.png", make_log_tile())
    write_png("forest/rock_small.png", make_rock(12, 8))
    write_png("forest/rock_big.png", make_rock(20, 12))
    write_png("forest/tuft_0.png", make_tuft(False))
    write_png("forest/tuft_1.png", make_tuft(True))
    write_png("forest/mote_0.png", make_mote(True))
    write_png("forest/mote_1.png", make_mote(False))
    print("Terminé.")


if __name__ == "__main__":
    sys.exit(main())
