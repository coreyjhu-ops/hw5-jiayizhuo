#!/bin/bash
set -e

REPO_NAME="hw5-jiayizhuo"
GITHUB_USER="coreyjhu-ops"

echo "🚀 推送 $REPO_NAME 到 GitHub..."
cd "$(dirname "$0")"

# 初始化 git
[ ! -d ".git" ] && git init && echo "✅ git init"

# 建 remote repo 并推送
gh repo create "$GITHUB_USER/$REPO_NAME" \
  --public \
  --description "JHU ISAI HW5 — Stock Advisor Skill: multi-perspective investment analysis (Buffett / Munger / Duan Yongping)" \
  --source=. \
  --remote=origin \
  --push 2>/dev/null || true

# 如果 remote 还没有，手动加
git remote get-url origin &>/dev/null || \
  git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"

git add .
echo ""
echo "📋 提交文件清单："
git status --short

git commit -m "feat: hw5 stock-advisor skill

Skill structure:
  .agents/skills/stock-advisor/
    SKILL.md        - skill trigger description and usage guide
    requirements.txt
    scripts/
      analyze_stock.py  - yfinance + bilingual HTML report generator

Analysis perspectives: Warren Buffett / Charlie Munger / Duan Yongping
Output: self-contained interactive HTML with CN/EN language toggle

JHU ISAI BU.330.760 Week 5 — Build a Reusable AI Skill" 2>/dev/null || \
  echo "（无新变更）"

git branch -M main
git push -u origin main

echo ""
echo "✅ 推送完成！"
echo "🔗 https://github.com/$GITHUB_USER/$REPO_NAME"
