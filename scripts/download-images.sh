#!/usr/bin/env bash
# 从网络下载彩灯/军事模型真实产品图到本地（网站运行时不再依赖外网）
# 请在 macOS「终端.app」执行（Cursor 内置终端可能因代理导致 403）:
#   cd /Users/lihui/chuangyi-lamp-website && bash scripts/download-images.sh
# 或使用 Python 脚本（推荐，带图片校验）:
#   python3 scripts/download-real-images.py

set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMGDIR="$ROOT/assets/images"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 清除代理
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
export NO_PROXY='*'
export no_proxy='*'

mkdir -p "$IMGDIR"
cd "$IMGDIR"

is_valid_image() {
  local f="$1"
  local sz
  sz=$(wc -c < "$f" | tr -d ' ')
  if [ "$sz" -lt 12000 ]; then
    return 1
  fi
  local magic
  magic=$(head -c 4 "$f" | xxd -p 2>/dev/null || true)
  case "$magic" in
    ffd8ff*) return 0 ;;
    89504e47*) return 0 ;;
  esac
  if head -c 1 "$f" | grep -q '<'; then
    return 1
  fi
  return 1
}

download() {
  local out="$1" url="$2"
  local tmp="${out}.download.tmp"
  echo "→ $out"
  rm -f "$tmp"
  if curl -fsSL --max-time 120 -A "$UA" \
    -H "Referer: https://commons.wikimedia.org/" \
    -o "$tmp" "$url" || \
     curl -fsSL --max-time 120 -A "$UA" -o "$tmp" "$url"; then
    if is_valid_image "$tmp"; then
      mv -f "$tmp" "$out"
      local sz
      sz=$(wc -c < "$out" | tr -d ' ')
      echo "  OK ($sz bytes)"
      return 0
    fi
    echo "  无效文件（非 JPEG/PNG 或过小），跳过"
    rm -f "$tmp"
  else
    echo "  下载失败"
    rm -f "$tmp"
  fi
  # 失败时保留原有 JPG，不删除
  return 1
}

echo "=== 彩灯 / 灯展（Wikimedia Commons 免费图）==="
download "hero-dragon.jpg"     "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1920px-Dragon_Lantern_Festival.jpg"
download "about-festival.jpg"  "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Qinhuai_Lantern_Festival_2018.jpg/1280px-Qinhuai_Lantern_Festival_2018.jpg"
download "lamp-festival.jpg"   "https://upload.wikimedia.org/wikipedia/commons/thumb/5/55/2025_Taiwan_Lantern_Festival_in_Taoyuan.jpg/1280px-2025_Taiwan_Lantern_Festival_in_Taoyuan.jpg"
download "lamp-park.jpg"         "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Seoul_Lantern_Festival_2014.jpg/1280px-Seoul_Lantern_Festival_2014.jpg"
download "lamp-folk.jpg"         "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/A_Colored_Rabbit_Lantern_at_Wong_Tai_Sin_Sik_Sik_Yuen.jpg/1280px-A_Colored_Rabbit_Lantern_at_Wong_Tai_Sin_Sik_Sik_Yuen.jpg"
download "lamp-dragon.jpg"       "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Dragon_Lantern_Festival.jpg/1280px-Dragon_Lantern_Festival.jpg"
download "lamp-decor.jpg"        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Fort_Worth_Botanic_Gardens_Lantern_Festival_2.jpg/1280px-Fort_Worth_Botanic_Gardens_Lantern_Festival_2.jpg"
download "lamp-custom.jpg"       "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/River_Phoenix_Lantern.jpg/1280px-River_Phoenix_Lantern.jpg"
download "lamp-landscape.jpg"    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/2017_Taiwan_Lantern_Festival%2C_Yunlin_%28Taiwan%29.jpg/1280px-2017_Taiwan_Lantern_Festival%2C_Yunlin_%28Taiwan%29.jpg"
download "lamp-national.jpg"     "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f1/2015_Taoyuan_Lantern_Festival.jpg/1280px-2015_Taoyuan_Lantern_Festival.jpg"

echo ""
echo "=== 军事模型 / 国防教育展陈 ==="
download "military-j20.jpg"      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/J-20_at_Airshow_China_2016.jpg/1280px-J-20_at_Airshow_China_2016.jpg"
download "military-tank.jpg"     "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/ZTZ-96_MBT_20131004.JPG/1280px-ZTZ-96_MBT_20131004.JPG"
download "military-carrier.jpg"  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Chinese_aircraft_carrier_Liaoning.jpg/1280px-Chinese_aircraft_carrier_Liaoning.jpg"
download "military-armor.jpg"    "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9c/Type_63_APC_at_the_Military_Museum_of_the_Chinese_People%27s_Revolution.jpg/1280px-Type_63_APC_at_the_Military_Museum_of_the_Chinese_People%27s_Revolution.jpg"
download "military-missile.jpg"  "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/DF-10A_in_Military_Parade_2015.jpg/1280px-DF-10A_in_Military_Parade_2015.jpg"
download "military-heli.jpg"     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/WZ-10_Attack_Helicopter.jpg/1280px-WZ-10_Attack_Helicopter.jpg"
download "military-edu.jpg"      "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Tank_Museum_China_2007_11.jpg/1280px-Tank_Museum_China_2007_11.jpg"
download "military-film.jpg"     "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/Reagans_with_USS_Ronald_Reagan_model_1996.jpg/1280px-Reagans_with_USS_Ronald_Reagan_model_1996.jpg"

echo ""
echo "已下载:"
ls -la *.jpg 2>/dev/null | awk '{print $5, $9}' || true
echo ""
echo "推荐优先执行: python3 scripts/download-real-images.py（爱采购 + Wikimedia，带校验）"
echo "完成。刷新 http://localhost:8765 查看。"
