#!/usr/bin/env python3
"""Construit les assets du jeu à partir du pack GandalfHardcore (references/).

- Compose le mage : peau + pantalon/chemise recolorés en marron + bottes + cheveux,
  puis découpe les animations (idle, walk, jump, cast, death) en frames ancrées
  bas-centre sur un canevas fixe.
- Découpe les éléments de scène : sol herbeux, plateformes, buissons, rochers,
  touffes, hautes herbes (cachettes), et copie arbres/fonds/nuages.

Usage : python3 tools/build_gandalf_assets.py
"""
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "sprites", "references", "Gandalf")
OUT = os.path.join(ROOT, "assets", "sprites", "gandalf")

CHAR_DIR = os.path.join(
    SRC, "GandalfHardcore FREE Character Asset Pack",
    "GandalfHardcore Character Asset Pack")
PLAT_DIR = os.path.join(SRC, "GandalfHardcore FREE Platformer Assets")
BG_DIR = os.path.join(PLAT_DIR, "GandalfHardcore Background layers", "Normal BG")


def load(path: str) -> Image.Image:
    return Image.open(path).convert("RGBA")


def save(img: Image.Image, rel: str) -> None:
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print(f"  {os.path.relpath(path, ROOT)}  ({img.width}x{img.height})")


def recolor_ramp(img: Image.Image, dark, light) -> Image.Image:
    """Remplace les teintes par une rampe marron pilotée par la luminance."""
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            lum = (r + g + b) / 765.0
            px[x, y] = tuple(
                int(d + (l - d) * lum) for d, l in zip(dark, light)
            ) + (a,)
    return out


def x_clusters(band: Image.Image, min_gap: int = 4, min_w: int = 6):
    """Regroupe les colonnes non vides en plages [x0, x1) (une par frame)."""
    alpha = band.split()[3]
    used = [False] * band.width
    apx = alpha.load()
    for x in range(band.width):
        for y in range(band.height):
            if apx[x, y] > 0:
                used[x] = True
                break
    runs = []
    x = 0
    while x < band.width:
        if used[x]:
            x0 = x
            while x < band.width and used[x]:
                x += 1
            runs.append([x0, x])
        else:
            x += 1
    merged = []
    for run in runs:
        if merged and run[0] - merged[-1][1] < min_gap:
            merged[-1][1] = run[1]
        else:
            merged.append(run)
    return [(x0, x1) for x0, x1 in merged if x1 - x0 >= min_w]


# --------------------------------------------------------------------------
# Le mage marron
# --------------------------------------------------------------------------
BROWN_ROBE = ((58, 42, 28), (154, 118, 78))
BROWN_PANTS = ((40, 28, 18), (110, 82, 54))

ANIM_ROWS = {"idle": 0, "walk": 1, "jump": 3, "cast": 5, "death": 6}
ROW_H = 64


def build_mage() -> None:
    skin = load(os.path.join(CHAR_DIR, "Character skin colors", "Male Skin1.png"))
    pants = recolor_ramp(
        load(os.path.join(CHAR_DIR, "Male Clothing", "Pants.png")), *BROWN_PANTS)
    shirt = recolor_ramp(
        load(os.path.join(CHAR_DIR, "Male Clothing", "Shirt.png")), *BROWN_ROBE)
    boots = load(os.path.join(CHAR_DIR, "Male Clothing", "Boots.png"))
    hair = load(os.path.join(CHAR_DIR, "Male Hair", "Male Hair1.png"))

    sheet = skin.copy()
    for layer in (pants, shirt, boots, hair):
        sheet.alpha_composite(layer)

    for anim, row in ANIM_ROWS.items():
        band = sheet.crop((0, row * ROW_H, sheet.width, (row + 1) * ROW_H))
        canvas_w = 52 if anim == "death" else 40
        canvas_h = 48
        for i, (x0, x1) in enumerate(x_clusters(band)):
            frame = band.crop((x0, 0, x1, ROW_H))
            bbox = frame.getbbox()
            frame = frame.crop(bbox)
            pad_bottom = ROW_H - bbox[3]  # pose aérienne : pieds décollés
            canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
            canvas.paste(
                frame,
                ((canvas_w - frame.width) // 2,
                 canvas_h - pad_bottom - frame.height),
            )
            save(canvas, f"player/mage_{anim}_{i}.png")


# --------------------------------------------------------------------------
# La scène
# --------------------------------------------------------------------------
def build_floor() -> None:
    tiles = load(os.path.join(PLAT_DIR, "Floor Tiles1.png"))
    block = tiles.crop((0, 0, 100, 110))
    bx = block.getbbox()
    # Bord solide : première ligne presque entièrement opaque (sous les brins).
    apx = block.split()[3].load()
    solid_top = None
    for y in range(bx[1], bx[3]):
        opaque = sum(1 for x in range(bx[0], bx[0] + 96) if apx[x, y] > 0)
        if opaque > 90:
            solid_top = y
            break
    assert solid_top is not None
    # Bande intérieure de 80 px : les bords du bloc source sont arrondis
    # (pixels transparents), on les évite pour un raccord sans couture.
    x0 = bx[0] + 8
    strip = tiles.crop((x0, solid_top - 6, x0 + 80, solid_top + 16))  # 80x22
    dirt = tiles.crop((x0, solid_top + 24, x0 + 80, solid_top + 48))  # 80x24

    # Sol : brins (6) + herbe (16) + terre (24) = 46 px de haut, bord solide à y=6.
    floor = Image.new("RGBA", (80, 46), (0, 0, 0, 0))
    floor.paste(strip, (0, 0))
    floor.paste(dirt, (0, 22))
    save(floor, "scene/floor.png")

    # Terre pleine pour les parois.
    save(dirt, "scene/dirt.png")

    # Plateforme flottante : 120 de large, bord solide à y=6, fond assombri.
    plat = Image.new("RGBA", (120, 28), (0, 0, 0, 0))
    for px_x in (0, 80):
        s = strip.crop((0, 0, min(80, 120 - px_x), 22))
        plat.paste(s, (px_x, 0))
        d = dirt.crop((0, 0, min(80, 120 - px_x), 6))
        plat.paste(d, (px_x, 22))
    ppx = plat.load()
    for x in range(plat.width):  # dernière ligne plus sombre
        r, g, b, a = ppx[x, 27]
        if a:
            ppx[x, 27] = (r * 2 // 5, g * 2 // 5, b * 2 // 5, a)
    save(plat, "scene/platform.png")


def crop_window_clusters(img: Image.Image, window, min_w: int = 10):
    """Découpe les éléments (plages x non vides) d'une fenêtre de la planche."""
    region = img.crop(window)
    crops = []
    for x0, x1 in x_clusters(region, min_gap=3, min_w=min_w):
        piece = region.crop((x0, 0, x1, region.height))
        crops.append(piece.crop(piece.getbbox()))
    return crops


def keep_main_y_cluster(img: Image.Image) -> Image.Image:
    """Ne garde que le plus grand bloc vertical (élimine les bouts d'éléments
    voisins attrapés par la fenêtre de découpe)."""
    apx = img.split()[3].load()
    used = [any(apx[x, y] > 0 for x in range(img.width))
            for y in range(img.height)]
    runs = []
    y = 0
    while y < img.height:
        if used[y]:
            y0 = y
            while y < img.height and used[y]:
                y += 1
            runs.append((y0, y))
        else:
            y += 1
    y0, y1 = max(runs, key=lambda r: r[1] - r[0])
    piece = img.crop((0, y0, img.width, y1))
    return piece.crop(piece.getbbox())


def build_props() -> None:
    decor = load(os.path.join(PLAT_DIR, "Decor.png"))
    # Buissons verts (bas-gauche de la planche).
    bushes = crop_window_clusters(decor, (0, 415, 175, 470), min_w=20)
    bushes.sort(key=lambda im: -im.width)
    save(bushes[0], "scene/bush.png")
    # Tas de rochers.
    rocks = crop_window_clusters(decor, (0, 255, 130, 330), min_w=30)
    rocks.sort(key=lambda im: -im.width)
    save(keep_main_y_cluster(rocks[0]), "scene/rock.png")
    # Petites touffes d'herbe.
    tufts = crop_window_clusters(decor, (0, 140, 120, 165), min_w=8)
    for i, tuft in enumerate(tufts[:2]):
        save(tuft, f"scene/tuft_{i}.png")

    # Cachette : grands roseaux du Decor (assez hauts pour couvrir le mage),
    # deux plants qui se chevauchent.
    reeds = crop_window_clusters(decor, (300, 130, 365, 200), min_w=15)
    reeds.sort(key=lambda im: -im.height)
    reed = reeds[0]
    step = reed.width - 10
    hide = Image.new("RGBA", (step + reed.width, reed.height), (0, 0, 0, 0))
    hide.alpha_composite(reed, (step, 0))
    hide.alpha_composite(reed.transpose(Image.FLIP_LEFT_RIGHT), (0, 0))
    save(hide, "scene/hide_grass.png")


def copy_backgrounds() -> None:
    save(load(os.path.join(BG_DIR, "GandalfHardcore Background layers_layer 5.png")),
         "scene/bg_sky.png")
    for n in (4, 3, 2, 1):
        save(load(os.path.join(
            BG_DIR, f"GandalfHardcore Background layers_layer {n}.png")),
            f"scene/bg_pines_{n}.png")
    save(load(os.path.join(PLAT_DIR, "Tree1.png")), "scene/tree_1.png")
    save(load(os.path.join(PLAT_DIR, "Tree2.png")), "scene/tree_2.png")
    save(load(os.path.join(PLAT_DIR, "cloud1.png")), "scene/cloud_1.png")
    save(load(os.path.join(PLAT_DIR, "cloud2.png")), "scene/cloud_2.png")


def main() -> None:
    print("Construction des assets Gandalf…")
    build_mage()
    build_floor()
    build_props()
    copy_backgrounds()
    print("Terminé.")


if __name__ == "__main__":
    sys.exit(main())
