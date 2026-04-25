#!/usr/bin/env python3
"""B4 — webapp smoke test"""
import os, sys, re
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp"

issues = []

data_js = WEBAPP / "data.js"
if not data_js.exists():
    issues.append("data.js 없음 — 03_build_webapp.py 먼저 실행")
else:
    content = data_js.read_text(encoding="utf-8")
    if "window.QUIZZES" not in content:
        issues.append("window.QUIZZES 정의 없음")
    m = re.search(r'"total"\s*:\s*(\d+)', content)
    if not m or int(m.group(1)) == 0:
        issues.append("meta.total 0 또는 누락")
    if '"ingredients"' not in content or '"topics"' not in content:
        issues.append("ingredients/topics 누락")

required = ["index.html", "dashboard.html", "question.html", "results.html", "app.js", "style.css"]
for f in required:
    if not (WEBAPP / f).exists():
        issues.append(f"{f} 없음")

if issues:
    print("❌ Smoke test FAIL:")
    for i in issues:
        print(f"  - {i}")
    sys.exit(1)
else:
    size = data_js.stat().st_size
    print(f"✅ Smoke test PASS — data.js {size:,} bytes")
    print(f"   webapp/index.html 더블클릭으로 동작 확인")
