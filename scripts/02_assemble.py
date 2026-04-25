#!/usr/bin/env python3
"""
A6 — 통합 + difficulty + reward_type 부여
- quizzes-from-docx.json (70) + quizzes-extras.json (30) = 100문제
- difficulty: style별 휴리스틱 (★/★★/★★★)
- reward_type: 가중 무작위 (collect 70 / steal 15 / gift 10 / swap 5)
  ※ 어려운 문제(★★★)에 특수 보상 우선 배치
- 최종 outputs/quizzes.json
"""
import os, sys, json, random
from pathlib import Path
from datetime import datetime

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
DOCX_JSON = ROOT / "outputs" / "quizzes-from-docx.json"
EXTRAS_JSON = ROOT / "outputs" / "quizzes-extras.json"
OUT = ROOT / "outputs" / "quizzes.json"

random.seed(42)  # 재현 가능

# 난이도 휴리스틱: style별 기본 난이도
DIFFICULTY_BY_STYLE = {
    "ox": 1,        # 가장 쉬움
    "mc": 1,        # 객관식 보통 쉬움
    "fill": 2,      # 빈칸 중급
    "nonsense": 2,  # 위트 필요
    "image": 2,     # 그림 보면 보통
    "open": 3,      # 한 문장 응답 어려움
    "apply": 3,     # 적용 가장 어려움
}

# 길이 기반 난이도 보정 (너무 긴 question은 +1)
def adjust_difficulty(quiz):
    base = DIFFICULTY_BY_STYLE.get(quiz["style"], 2)
    qlen = len(quiz.get("question", ""))
    if qlen > 70:
        base = min(3, base + 1)
    return base


def assign_reward_types(quizzes):
    """
    분포 — collect 70%, steal 15%, gift 10%, swap 5%
    어려운 문제(difficulty=3)에 특수 보상(steal/gift/swap) 우선
    """
    n = len(quizzes)
    n_steal = round(n * 0.15)
    n_gift = round(n * 0.10)
    n_swap = round(n * 0.05)
    n_collect = n - n_steal - n_gift - n_swap

    # 우선순위: difficulty 3 → 2 → 1 순으로 특수 보상 배정
    indexed = list(enumerate(quizzes))
    sorted_by_diff = sorted(indexed, key=lambda x: -x[1]["difficulty"])

    reward = [None] * n
    pool = ["steal"] * n_steal + ["gift"] * n_gift + ["swap"] * n_swap
    random.shuffle(pool)

    # 어려운 순서로 특수 보상 부여
    for (idx, _), rtype in zip(sorted_by_diff, pool):
        reward[idx] = rtype
    # 나머지는 collect
    for i in range(n):
        if reward[i] is None:
            reward[i] = "collect"

    return reward


def main():
    if not DOCX_JSON.exists():
        print(f"❌ {DOCX_JSON} not found"); sys.exit(1)
    if not EXTRAS_JSON.exists():
        print(f"❌ {EXTRAS_JSON} not found"); sys.exit(1)

    docx_data = json.loads(DOCX_JSON.read_text(encoding="utf-8"))
    extras_data = json.loads(EXTRAS_JSON.read_text(encoding="utf-8"))

    all_quizzes = docx_data["quizzes"] + extras_data["quizzes"]
    print(f"📥 합계 {len(all_quizzes)}문제 (DOCX {len(docx_data['quizzes'])} + extras {len(extras_data['quizzes'])})")

    # difficulty 부여
    for q in all_quizzes:
        q["difficulty"] = adjust_difficulty(q)

    # reward_type 부여 (특수 보상은 어려운 문제 우선)
    rewards = assign_reward_types(all_quizzes)
    for q, r in zip(all_quizzes, rewards):
        q["reward_type"] = r

    # 통계
    by_style = {}
    by_topic = {}
    by_diff = {}
    by_reward = {}
    for q in all_quizzes:
        by_style[q["style"]] = by_style.get(q["style"], 0) + 1
        by_topic[q["topic_id"]] = by_topic.get(q["topic_id"], 0) + 1
        by_diff[q["difficulty"]] = by_diff.get(q["difficulty"], 0) + 1
        by_reward[q["reward_type"]] = by_reward.get(q["reward_type"], 0) + 1

    output = {
        "meta": {
            "title": "2026 봄 드림아동부 교리퀴즈대회",
            "date_planned": "2026-04-19",
            "source": "DOCX 자료1 (70) + Claude 신규 생성 extras (30)",
            "generated_at": datetime.now().isoformat(),
            "total": len(all_quizzes),
            "by_style": by_style,
            "by_topic": by_topic,
            "by_difficulty": {f"★{k}": v for k, v in sorted(by_diff.items())},
            "by_reward_type": by_reward,
        },
        "quizzes": all_quizzes,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n✅ 통합 완료: {OUT}")
    print(f"   total: {len(all_quizzes)}")
    print(f"   by_style:    {by_style}")
    print(f"   by_topic:    {by_topic}")
    print(f"   by_difficulty: {dict(sorted(by_diff.items()))}")
    print(f"   by_reward:   {by_reward}")


if __name__ == "__main__":
    main()
