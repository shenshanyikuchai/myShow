#!/usr/bin/env python3
"""本地生成彩灯/军事模型产品展示图（Pillow），无需外网。"""

from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
W, H = 1280, 800


def gradient_bg(draw: ImageDraw.ImageDraw, colors: list[tuple], vertical: bool = True) -> None:
    for i in range(H):
        t = i / H if vertical else 0
        if vertical:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * t)
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * t)
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * t)
            draw.line([(0, i), (W, i)], fill=(r, g, b))
        break


def new_canvas(c1: tuple, c2: tuple) -> Image.Image:
    img = Image.new("RGB", (W, H), c1)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def add_glow(img: Image.Image, cx: int, cy: int, radius: int, color: tuple, alpha: int = 80) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for r in range(radius, 0, -8):
        a = int(alpha * (r / radius) ** 2)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], a))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, layer).convert("RGB")


def draw_lantern(d: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, color: tuple) -> None:
    d.ellipse([x, y, x + w, y + h], fill=color)
    d.rectangle([x + w // 4, y + h, x + 3 * w // 4, y + h + 12], fill=(255, 200, 60))
    d.line([x + w // 2, y - 20, x + w // 2, y], fill=(255, 200, 60), width=3)


def draw_dragon_silhouette(d: ImageDraw.ImageDraw) -> None:
    pts = [
        (200, 500), (280, 320), (400, 380), (520, 260), (680, 300),
        (820, 220), (980, 280), (900, 420), (720, 480), (500, 520), (200, 500),
    ]
    d.polygon(pts, fill=(255, 80, 60))
    d.polygon([(820, 220), (1050, 200), (980, 280)], fill=(255, 180, 50))


def draw_tank(d: ImageDraw.ImageDraw) -> None:
    d.rounded_rectangle([280, 380, 1000, 520], radius=20, fill=(70, 80, 95))
    d.rounded_rectangle([420, 300, 780, 400], radius=12, fill=(90, 100, 115))
    d.rounded_rectangle([520, 260, 680, 310], fill=(110, 120, 135))
    for cx in (380, 560, 740, 900):
        d.ellipse([cx - 45, 500, cx + 45, 590], fill=(40, 45, 55), outline=(0, 230, 255), width=3)


def draw_jet(d: ImageDraw.ImageDraw) -> None:
    d.polygon([(200, 420), (640, 280), (1100, 400), (900, 460), (640, 400), (200, 420)], fill=(80, 90, 105))
    d.polygon([(640, 280), (720, 200), (800, 280)], fill=(100, 110, 125))
    d.line([(300, 400), (150, 480)], fill=(0, 230, 255), width=4)
    d.line([(900, 420), (1050, 500)], fill=(0, 230, 255), width=4)


def draw_carrier(d: ImageDraw.ImageDraw) -> None:
    d.polygon([(120, 480), (1160, 480), (1100, 420), (180, 420)], fill=(65, 75, 90))
    d.rectangle([200, 380, 1000, 420], fill=(85, 95, 110))
    d.polygon([(400, 380), (440, 300), (520, 380)], fill=(100, 110, 125))


def draw_heli(d: ImageDraw.ImageDraw) -> None:
    d.ellipse([440, 360, 840, 480], fill=(75, 85, 100))
    d.ellipse([560, 320, 740, 400], fill=(95, 105, 120))
    d.line([(200, 380), (1080, 380)], fill=(0, 230, 255), width=5)
    d.line([(640, 200), (640, 320)], fill=(120, 130, 145), width=6)


def draw_missile_truck(d: ImageDraw.ImageDraw) -> None:
    d.rounded_rectangle([200, 440, 1050, 520], radius=10, fill=(70, 80, 95))
    for i, ox in enumerate([280, 480, 680]):
        d.rounded_rectangle([ox, 360, ox + 120, 460], radius=6, fill=(90, 100, 115))
        d.polygon([ox + 50, 360, ox + 70, 280, ox + 90, 360], fill=(120, 130, 145))
    d.ellipse([320, 520, 400, 600], fill=(40, 45, 55))
    d.ellipse([880, 520, 960, 600], fill=(40, 45, 55))


def draw_apc(d: ImageDraw.ImageDraw) -> None:
    d.rounded_rectangle([300, 380, 980, 500], radius=16, fill=(75, 85, 100))
    d.rounded_rectangle([380, 320, 720, 400], fill=(95, 105, 120))
    d.ellipse([360, 490, 460, 590], fill=(45, 50, 60), outline=(180, 120, 255), width=3)
    d.ellipse([760, 490, 860, 590], fill=(45, 50, 60), outline=(180, 120, 255), width=3)


def draw_museum_row(d: ImageDraw.ImageDraw) -> None:
    draw_tank(d)
    d.rounded_rectangle([80, 120, 400, 200], fill=(255, 200, 60, 0))
    d.rectangle([100, 140, 380, 180], fill=(20, 15, 30))
    d.text((120, 148), "国防教育基地", fill=(255, 200, 60))


def draw_film_set(d: ImageDraw.ImageDraw) -> None:
    d.rounded_rectangle([280, 200, 1000, 560], radius=12, outline=(255, 100, 80), width=4)
    d.ellipse([560, 320, 720, 440], fill=(30, 25, 40), outline=(255, 200, 60), width=4)
    d.polygon([(620, 360), (620, 400), (660, 380)], fill=(255, 200, 60))


def title(draw: ImageDraw.ImageDraw, text: str, sub: str = "") -> None:
    try:
        font_l = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 42)
        font_s = ImageFont.truetype("/System/Library/Fonts/STHeiti Light.ttc", 24)
    except OSError:
        font_l = ImageFont.load_default()
        font_s = font_l
    draw.text((60, H - 120), text, fill=(255, 220, 100), font=font_l)
    if sub:
        draw.text((60, H - 65), sub, fill=(180, 170, 190), font=font_s)


def save(name: str, img: Image.Image) -> None:
    path = OUT / name
    img.save(path, "JPEG", quality=88, optimize=True)
    print(f"  {name} ({path.stat().st_size:,} bytes)")


def gen_lamp(name: str, title_text: str, fn) -> None:
    img = new_canvas((18, 8, 28), (8, 12, 32))
    img = add_glow(img, W // 2, H // 3, 280, (255, 80, 50), 60)
    d = ImageDraw.Draw(img)
    fn(d)
    title(d, title_text, "河南创亿彩灯艺术有限公司")
    save(name, img)


def gen_military(name: str, title_text: str, fn) -> None:
    img = new_canvas((8, 14, 28), (12, 8, 22))
    img = add_glow(img, W // 2, H // 2, 220, (0, 230, 255), 45)
    d = ImageDraw.Draw(img)
    fn(d)
    title(d, title_text, "仿真模型 · 国防教育展陈")
    save(name, img)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("生成本地产品 JPG ...")

    gen_lamp("hero-dragon.jpg", "龙年彩灯 · 光影盛宴", lambda d: draw_dragon_silhouette(d))
    gen_lamp("about-festival.jpg", "节日彩灯花灯", lambda d: (
        draw_lantern(d, 200, 280, 90, 110, (230, 60, 50)),
        draw_lantern(d, 420, 260, 110, 130, (255, 100, 60)),
        draw_lantern(d, 680, 280, 90, 110, (230, 60, 50)),
    ))
    gen_lamp("lamp-festival.jpg", "节日彩灯", lambda d: (
        draw_lantern(d, 180, 250, 100, 120, (255, 70, 50)),
        draw_lantern(d, 400, 230, 120, 140, (255, 120, 60)),
        draw_lantern(d, 650, 250, 100, 120, (255, 70, 50)),
    ))
    gen_lamp("lamp-park.jpg", "公园景观灯", lambda d: (
        [d.ellipse([x, 200, x + 16, 216], fill=(255, 200, 60)) for x in range(100, 1100, 50)],
        d.rectangle([0, 520, W, H], fill=(15, 25, 35)),
    ))
    gen_lamp("lamp-folk.jpg", "民俗花灯 · 兔子彩灯", lambda d: (
        d.ellipse([520, 300, 720, 480], fill=(255, 120, 150)),
        d.ellipse([560, 240, 660, 300], fill=(255, 120, 150)),
        d.ellipse([580, 360, 600, 380], fill=(255, 255, 255)),
        d.ellipse([620, 360, 640, 380], fill=(255, 255, 255)),
    ))
    gen_lamp("lamp-dragon.jpg", "大型龙形花灯灯组", draw_dragon_silhouette)
    gen_lamp("lamp-decor.jpg", "装饰花灯", lambda d: (
        [draw_lantern(d, 120 + i * 180, 260, 70, 85, (220, 50 + i * 15, 50)) for i in range(5)],
    ))
    gen_lamp("lamp-custom.jpg", "彩灯定制设计", lambda d: (
        d.rounded_rectangle([360, 220, 920, 520], radius=8, outline=(0, 230, 255), width=3),
        d.line([(360, 220), (920, 520)], fill=(255, 100, 60), width=2),
        d.line([(920, 220), (360, 520)], fill=(255, 100, 60), width=2),
    ))
    gen_lamp("lamp-landscape.jpg", "景观花灯", lambda d: (
        [d.ellipse([150 + i * 200, 280, 250 + i * 200, 380], fill=(255, 80 + i * 10, 50)) for i in range(4)],
    ))
    gen_lamp("lamp-national.jpg", "国庆节主题彩灯", lambda d: (
        d.rectangle([540, 240, 740, 480], fill=(200, 30, 40)),
        [d.ellipse([cx, cy, cx + 20, cy + 20], fill=(255, 200, 60)) for cx, cy in [(580, 280), (620, 320), (660, 360), (600, 360), (640, 400)]],
    ))

    gen_military("military-j20.jpg", "歼-20 战斗机模型", draw_jet)
    gen_military("military-tank.jpg", "主战坦克模型", draw_tank)
    gen_military("military-carrier.jpg", "航母军舰模型", draw_carrier)
    gen_military("military-armor.jpg", "装甲战车模型", draw_apc)
    gen_military("military-missile.jpg", "导弹发射车模型", draw_missile_truck)
    gen_military("military-heli.jpg", "武装直升机模型", draw_heli)
    gen_military("military-edu.jpg", "国防教育基地套装", draw_museum_row)
    gen_military("military-film.jpg", "影视军事道具", draw_film_set)

    print("完成。")


if __name__ == "__main__":
    main()
