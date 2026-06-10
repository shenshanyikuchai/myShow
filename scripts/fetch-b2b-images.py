#!/usr/bin/env python3
"""
从百度爱采购等同类企业店铺抓取产品图，保存到 assets/images/（网站运行时仅用本地文件）。

用法（需联网）:
  python3 scripts/fetch-b2b-images.py
  python3 scripts/fetch-b2b-images.py --shop 58102899   # 河南创亿彩灯艺术有限公司
"""

from __future__ import annotations

import argparse
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "images"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

# 彩灯店铺 + 军事模型类店铺（同类河南/中原企业）
SHOPS = {
    "58102899": "河南创亿彩灯艺术有限公司",
    "11467": "赏艺模型（军事模型参考）",
}

# 产品图文件名与关键词（从店铺商品标题匹配）
LAMP_SLOTS = [
    ("hero-dragon.jpg", ["龙", "花灯", "彩灯", "灯展"]),
    ("about-festival.jpg", ["节日", "元宵", "春节", "花灯"]),
    ("lamp-festival.jpg", ["节日", "元宵", "春节"]),
    ("lamp-park.jpg", ["公园", "景观", "亮化"]),
    ("lamp-folk.jpg", ["民俗", "兔子", "传统"]),
    ("lamp-dragon.jpg", ["龙", "大型"]),
    ("lamp-decor.jpg", ["装饰", "道具", "灯笼"]),
    ("lamp-custom.jpg", ["定制", "设计"]),
    ("lamp-landscape.jpg", ["景观", "夜游"]),
    ("lamp-national.jpg", ["国庆", "红旗"]),
]

MILITARY_SLOTS = [
    ("military-j20.jpg", ["歼", "战斗机", "战机", "J-20", "j20"]),
    ("military-tank.jpg", ["坦克", "99", "96"]),
    ("military-carrier.jpg", ["航母", "军舰", "辽宁"]),
    ("military-armor.jpg", ["装甲", "战车", "步兵"]),
    ("military-missile.jpg", ["导弹", "东风", "发射"]),
    ("military-heli.jpg", ["直升机", "武直"]),
    ("military-edu.jpg", ["国防", "教育", "研学", "基地"]),
    ("military-film.jpg", ["影视", "道具", "置景"]),
]

IMG_RE = re.compile(
    r"https?://[^\s\"'<>]+?\.(?:jpg|jpeg|png|webp)(?:\?[^\s\"'<>]*)?",
    re.I,
)
BCEBOS_RE = re.compile(r"//[a-z0-9.-]+\.bcebos\.com/[^\s\"'<>]+", re.I)


def fetch(url: str, timeout: int = 30) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
        return resp.read()


def normalize_url(u: str) -> str:
    u = u.strip()
    if u.startswith("//"):
        return "https:" + u
    return u


def extract_images(html: str) -> list[str]:
    found: list[str] = []
    for m in IMG_RE.finditer(html):
        found.append(normalize_url(m.group(0)))
    for m in BCEBOS_RE.finditer(html):
        found.append(normalize_url(m.group(0)))
    # 去重保序
    seen: set[str] = set()
    out: list[str] = []
    for u in found:
        if u not in seen and "logo" not in u.lower() and "favicon" not in u.lower():
            seen.add(u)
            out.append(u)
    return out


def shop_urls(xzhid: str) -> list[str]:
    name = SHOPS.get(xzhid, "")
    enc = urllib.parse.quote(name) if name else ""
    return [
        f"https://b2b.baidu.com/shop?name={enc}&xzhid={xzhid}",
        f"https://b2b.baidu.com/m/aitf/s/shop?xzhid={xzhid}",
        f"https://b2b.baidu.com/s?q={urllib.parse.quote('彩灯')}&from=search",
        f"https://b2b.baidu.com/s?q={urllib.parse.quote('军事模型')}&from=search",
    ]


def search_api_images(query: str) -> list[str]:
    """尝试爱采购开放页面中的商品图。"""
    urls: list[str] = []
    q = urllib.parse.quote(query)
    for page_url in [
        f"https://b2b.baidu.com/s?q={q}&from=search",
        f"https://b2b.baidu.com/s?q={q}",
    ]:
        try:
            html = fetch(page_url).decode("utf-8", errors="ignore")
            urls.extend(extract_images(html))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  跳过 {page_url}: {e}")
    return urls


def score_title(title: str, keywords: list[str]) -> int:
    t = title.lower()
    return sum(1 for k in keywords if k.lower() in t or k in title)


def is_valid_image(data: bytes) -> bool:
    if len(data) < 12000:
        return False
    if data[:3] == b"\xff\xd8\xff":
        return True
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    head = data[:200].lstrip()
    if head.startswith(b"<") or b"<html" in data[:500].lower():
        return False
    return False


def download_file(url: str, dest: Path) -> bool:
    try:
        data = fetch(url)
        if not is_valid_image(data):
            print(f"  跳过 {dest.name}: 非有效图片（可能是 HTML/CSS）")
            return False
        dest.write_bytes(data)
        print(f"  OK {dest.name} ({len(data)} bytes) <- {url[:80]}...")
        return True
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        print(f"  失败 {dest.name}: {e}")
        return False


def assign_slots(
    slots: list[tuple[str, list[str]]],
    pool: list[str],
    used_urls: set[str],
) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for filename, keywords in slots:
        for url in pool:
            if url in used_urls:
                continue
            # 用 URL 路径做简单关键词匹配
            path = url.lower()
            if any(k.lower() in path for k in keywords) or keywords[0] in path:
                mapping[filename] = url
                used_urls.add(url)
                break
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shop", default="58102899", help="爱采购 xzhid")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)

    print("采集图片链接…")
    pool: list[str] = []

    for url in shop_urls(args.shop):
        try:
            html = fetch(url).decode("utf-8", errors="ignore")
            imgs = extract_images(html)
            print(f"  {url}: {len(imgs)} 张")
            pool.extend(imgs)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  {url}: 失败 {e}")

    for q in ["彩灯花灯", "龙年彩灯", "节日彩灯", "军事模型", "坦克模型", "歼20模型"]:
        pool.extend(search_api_images(q))

    # Wikimedia 备用（部分网络可访问）
    wikimedia = [
        ("hero-dragon.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1280px-Dragon_Lantern_Festival.jpg"),
        ("lamp-dragon.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1280px-Dragon_Lantern_Festival.jpg"),
        ("military-j20.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/J-20_at_Airshow_China_2016.jpg/1280px-J-20_at_Airshow_China_2016.jpg"),
        ("military-tank.jpg", "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/ZTZ-96_MBT_20131004.JPG/1280px-ZTZ-96_MBT_20131004.JPG"),
    ]

    seen: set[str] = set()
    unique_pool: list[str] = []
    for u in pool:
        if u not in seen:
            seen.add(u)
            unique_pool.append(u)

    print(f"共 {len(unique_pool)} 个候选链接")

    used: set[str] = set()
    lamp_map = assign_slots(LAMP_SLOTS, unique_pool, used)
    mil_map = assign_slots(MILITARY_SLOTS, unique_pool, used)

    ok = 0
    for filename, keywords in LAMP_SLOTS + MILITARY_SLOTS:
        dest = OUT / filename
        if filename in lamp_map:
            if download_file(lamp_map[filename], dest):
                ok += 1
            continue
        if filename in mil_map:
            if download_file(mil_map[filename], dest):
                ok += 1
            continue
        # 按序消耗剩余 pool
        for url in unique_pool:
            if url in used:
                continue
            used.add(url)
            if download_file(url, dest):
                ok += 1
                break

    for filename, url in wikimedia:
        dest = OUT / filename
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        if download_file(url, dest):
            ok += 1

    print(f"\n完成: 成功下载/更新 {ok} 张。缺失文件可运行: python3 scripts/generate-images.py")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
