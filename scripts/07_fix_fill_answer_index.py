#!/usr/bin/env python3
"""빈칸(fill) 문제의 answer_text와 options[i]를 매칭해서 answer_index 부여"""
import os, sys, json
from pathlib import Path
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
QUIZZES = ROOT / "outputs" / "quizzes.json"

data = json.loads(QUIZZES.read_text(encoding="utf-8"))
fixed = 0
for q in data["quizzes"]:
    if q["style"] == "fill" and q.get("answer_index") is None and q.get("options"):
        ans = (q.get("answer_text") or "").strip()
        # options에서 정확 매칭 우선
        for i, opt in enumerate(q["options"]):
            if opt.strip() == ans:
                q["answer_index"] = i
                fixed += 1
                break
        # 정확 매칭 실패 시 부분 매칭
        if q.get("answer_index") is None:
            for i, opt in enumerate(q["options"]):
                if ans in opt or opt in ans:
                    q["answer_index"] = i
                    fixed += 1
                    break

QUIZZES.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"✅ 빈칸 자동채점 복구: {fixed}개")
