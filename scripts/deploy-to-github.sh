#!/usr/bin/env bash
# 部署到 https://github.com/shenshanyikuchai/myShow
# 在 macOS「终端.app」执行（需已登录 GitHub）:
#   bash scripts/deploy-to-github.sh
# 若远程为旧版个人站、需完全替换为本企业站:
#   FORCE_DEPLOY=1 bash scripts/deploy-to-github.sh

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "未找到 git 仓库。"
  exit 1
fi

git fetch origin main

if [ "${FORCE_DEPLOY:-}" = "1" ]; then
  echo "→ 强制推送（用本网站覆盖远程 main，--force-with-lease）…"
  git push --force-with-lease -u origin main
else
  echo "→ 尝试合并远程历史后推送…"
  if ! git merge-base --is-ancestor origin/main HEAD 2>/dev/null; then
    git pull origin main --allow-unrelated-histories --no-edit || {
      echo ""
      echo "合并失败。若要用彩灯企业站完全替换旧个人站，请执行:"
      echo "  FORCE_DEPLOY=1 bash scripts/deploy-to-github.sh"
      exit 1
    }
  fi
  git push -u origin main || {
    echo ""
    echo "推送被拒（历史不相关）。请执行:"
    echo "  FORCE_DEPLOY=1 bash scripts/deploy-to-github.sh"
    exit 1
  }
fi

echo ""
echo "完成！仓库: https://github.com/shenshanyikuchai/myShow"
echo "GitHub Pages: Settings → Pages → Branch: main / 根目录"
echo "站点地址: https://shenshanyikuchai.github.io/myShow/"
