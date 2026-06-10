#!/usr/bin/env python3
"""
下载真实彩灯 / 军事模型产品图到 assets/images/（网站运行时仅用本地文件）。

请在 macOS「终端.app」中执行（勿在 Cursor 内置终端，避免代理 403）:
  cd /Users/lihui/chuangyi-lamp-website
  python3 scripts/download-real-images.py

来源优先级:
  1. 百度爱采购（河南创亿及同类彩灯/军事模型企业商品图）
  2. Wikimedia Commons 灯展 / 国防展陈实景图
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 清除代理，避免 Cursor/IDE 注入的 127.0.0.1 代理导致 CONNECT 403
for _k in (
    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
    "http_proxy", "https_proxy", "all_proxy",
):
    os.environ.pop(_k, None)
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

SHOP_XZHID = "58102899"
SHOP_NAME = "河南创亿彩灯艺术有限公司"

IMG_RE = re.compile(
    r"https?://[^\s\"'<>\\]+?\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"'<>\\]*)?",
    re.I,
)
BCEBOS_RE = re.compile(
    r"https?://[a-z0-9.-]+\.bcebos\.com/[^\s\"'<>\\]+",
    re.I,
)

# 每个文件名对应多个候选 URL（Wikimedia 灯展/军事实景）
CURATED: dict[str, list[str]] = {
    "hero-dragon.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1920px-Dragon_Lantern_Festival.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/7/7b/Dragon_Lantern_Festival.jpg",
    ],
    "about-festival.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Qinhuai_Lantern_Festival_2018.jpg/1280px-Qinhuai_Lantern_Festival_2018.jpg",
    ],
    "lamp-festival.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/2025_Taiwan_Lantern_Festival_in_Taoyuan.jpg/1280px-2025_Taiwan_Lantern_Festival_in_Taoyuan.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/2015_Taoyuan_Lantern_Festival.jpg/1280px-2015_Taoyuan_Lantern_Festival.jpg",
    ],
    "lamp-park.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Seoul_Lantern_Festival_2014.jpg/1280px-Seoul_Lantern_Festival_2014.jpg",
    ],
    "lamp-folk.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/A_Colored_Rabbit_Lantern_at_Wong_Tai_Sin_Sik_Sik_Yuen.jpg/1280px-A_Colored_Rabbit_Lantern_at_Wong_Tai_Sin_Sik_Sik_Yuen.jpg",
    ],
    "lamp-dragon.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1280px-Dragon_Lantern_Festival.jpg",
    ],
    "lamp-decor.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Fort_Worth_Botanic_Gardens_Lantern_Festival_2.jpg/1280px-Fort_Worth_Botanic_Gardens_Lantern_Festival_2.jpg",
    ],
    "lamp-custom.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/River_Phoenix_Lantern.jpg/1280px-River_Phoenix_Lantern.jpg",
    ],
    "lamp-landscape.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/2017_Taiwan_Lantern_Festival%2C_Yunlin_%28Taiwan%29.jpg/1280px-2017_Taiwan_Lantern_Festival%2C_Yunlin_%28Taiwan%29.jpg",
    ],
    "lamp-national.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/2015_Taoyuan_Lantern_Festival.jpg/1280px-2015_Taoyuan_Lantern_Festival.jpg",
    ],
    "military-j20.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/J-20_at_Airshow_China_2016.jpg/1280px-J-20_at_Airshow_China_2016.jpg",
    ],
    "military-tank.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/ZTZ-96_MBT_20131004.JPG/1280px-ZTZ-96_MBT_20131004.JPG",
    ],
    "military-carrier.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Chinese_aircraft_carrier_Liaoning.jpg/1280px-Chinese_aircraft_carrier_Liaoning.jpg",
    ],
    "military-armor.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Type_63_APC_at_the_Military_Museum_of_the_Chinese_People%27s_Revolution.jpg/1280px-Type_63_APC_at_the_Military_Museum_of_the_Chinese_People%27s_Revolution.jpg",
    ],
    "military-missile.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/DF-10A_in_Military_Parade_2015.jpg/1280px-DF-10A_in_Military_Parade_2015.jpg",
    ],
    "military-heli.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/WZ-10_Attack_Helicopter.jpg/1280px-WZ-10_Attack_Helicopter.jpg",
    ],
    "military-edu.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Tank_Museum_China_2007_11.jpg/1280px-Tank_Museum_China_2007_11.jpg",
    ],
    "military-film.jpg": [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Reagans_with_USS_Ronald_Reagan_model_1996.jpg/1280px-Reagans_with_USS_Ronald_Reagan_model_1996.jpg",
    ],
}

SEARCH_QUERIES = [
    "彩灯花灯", "龙年彩灯", "节日彩灯", "河南彩灯",
    "军事模型", "坦克模型", "歼20模型", "国防教育模型",
]


def is_valid_image(data: bytes) -> bool:
    if len(data) < 12000:
        return False
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    # 拒绝 HTML/CSS 误存为 jpg
    head = data[:200].lstrip()
    if head.startswith(b"<") or head.startswith(b".") or b"<html" in head[:500].lower():
        return False
    return False


def curl_bytes(url: str, referer: str | None = None) -> bytes | None:
    headers = ["-H", f"User-Agent: {UA}"]
    if referer:
        headers.extend(["-H", f"Referer: {referer}"])
    cmd = [
        "curl", "-fsSL", "--max-time", "90",
        *headers,
        url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=100)
        if r.returncode != 0:
            return None
        return r.stdout
    except (subprocess.TimeoutExpired, OSError):
        return None


def curl_html(url: str) -> str:
    data = curl_bytes(url, referer="https://b2b.baidu.com/")
    if not data:
        return ""
    return data.decode("utf-8", errors="ignore")


def extract_image_urls(html: str) -> list[str]:
    found: list[str] = []
    for pat in (IMG_RE, BCEBOS_RE):
        for m in pat.finditer(html):
            u = m.group(0).strip()
            if u.startswith("//"):
                u = "https:" + u
            low = u.lower()
            if any(x in low for x in ("logo", "favicon", "icon", "loading", "avatar")):
                continue
            found.append(u)
    seen: set[str] = set()
    out: list[str] = []
    for u in found:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def scrape_b2b_pool() -> list[str]:
    pool: list[str] = []
    enc_name = urllib.parse.quote(SHOP_NAME)
    pages = [
        f"https://b2b.baidu.com/shop?name={enc_name}&xzhid={SHOP_XZHID}",
        f"https://b2b.baidu.com/m/aitf/s/shop?xzhid={SHOP_XZHID}",
    ]
    for q in SEARCH_QUERIES:
        pages.append(f"https://b2b.baidu.com/s?q={urllib.parse.quote(q)}&from=search")

    for url in pages:
        html = curl_html(url)
        imgs = extract_image_urls(html)
        print(f"  {url[:70]}… → {len(imgs)} 张")
        pool.extend(imgs)
    return pool


def save_image(dest: Path, data: bytes) -> bool:
    if not is_valid_image(data):
        return False
    dest.write_bytes(data)
    return True


def download_to(dest: Path, url: str, referer: str | None = None) -> bool:
    data = curl_bytes(url, referer=referer)
    if not data:
        return False
    if save_image(dest, data):
        print(f"  ✓ {dest.name} ({len(data):,} bytes) ← {url[:72]}…")
        return True
    return False


def try_urls(dest: Path, urls: list[str], referer: str | None = None) -> bool:
    for url in urls:
        if download_to(dest, url, referer=referer):
            return True
    return False


def assign_b2b_images(pool: list[str], filenames: list[str]) -> dict[str, str]:
    """将爱采购商品图按序分配给尚未下载的文件。"""
    mapping: dict[str, str] = {}
    used: set[str] = set()
    idx = 0
    for name in filenames:
        while idx < len(pool):
            url = pool[idx]
            idx += 1
            if url in used:
                continue
            used.add(url)
            mapping[name] = url
            break
    return mapping


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    all_names = list(CURATED.keys())

    print("=== 1. 采集百度爱采购商品图链接 ===")
    pool = scrape_b2b_pool()
    print(f"候选链接共 {len(pool)} 个\n")

    b2b_map = assign_b2b_images(pool, all_names)

    print("=== 2. 下载真实图片（校验 JPEG/PNG，拒绝 HTML）===")
    ok = 0
    for name in all_names:
        dest = OUT / name
        print(f"→ {name}")

        if name in b2b_map:
            if download_to(dest, b2b_map[name], referer="https://b2b.baidu.com/"):
                ok += 1
                continue

        if try_urls(dest, CURATED[name], referer="https://commons.wikimedia.org/"):
            ok += 1
            continue

        print(f"  ✗ 全部来源失败，保留现有文件")

    print(f"\n成功更新 {ok}/{len(all_names)} 张真实照片。")
    if ok < len(all_names):
        print("未成功的文件可稍后重试，或运行: python3 scripts/generate-images.py（示意占位图）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
