#!/usr/bin/env python3
"""
A3 — 자료1 DOCX 파서
inputs/source.docx → outputs/quizzes-from-docx.json (5종 형식 원형 복원)

추출 대상:
- 5개 과 (성경/신/기독/성령/종말)
- 각 과 14문제 (객관식 6 + OX 4 + 빈칸 1 + 주관식 1 + 적용 1 + α)
- 정답·해설·성경 구절 동반
"""
import os, sys, re, json
from pathlib import Path
from datetime import datetime

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")
import docx

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "inputs" / "source.docx"
OUT = ROOT / "outputs" / "quizzes-from-docx.json"

# topic_id 매핑 (state.yaml과 일치)
TOPIC_MAP = {
    1: "bibliology",
    2: "theology_proper",
    3: "christology",
    4: "pneumatology",
    5: "soteriology",
    6: "ecclesiology",
    7: "eschatology",
}

# 스타일 추출 정규식 (DOCX 라벨 → 우리 style id)
STYLE_MAP = {
    "객관식": "mc",
    "OX": "ox",
    "빈칸": "fill",
    "주관식": "open",
    "적용": "apply",
}


def split_into_lessons(paras):
    """과 단위로 분할. 반환: [(lesson_no, [paragraphs]), ...]"""
    lessons = []
    current_no = None
    current_paras = []
    for p in paras:
        # "제N과." (마침표) 또는 "제N과," (쉼표) 둘 다 인식
        m = re.match(r"^제(\d+)과[\.\,]\s*", p.strip())
        if m:
            if current_no is not None:
                lessons.append((current_no, current_paras))
            current_no = int(m.group(1))
            current_paras = [p]
        else:
            current_paras.append(p)
    if current_no is not None:
        lessons.append((current_no, current_paras))
    return lessons


def extract_quiz_section(lesson_paras):
    """과 안에서 'Ⅲ. N과 교리퀴즈' 이후 부분만 추출"""
    in_quiz = False
    quiz_paras = []
    for p in lesson_paras:
        if re.search(r"Ⅲ\.\s*\d+과\s*교리퀴즈", p):
            in_quiz = True
            continue
        if in_quiz:
            quiz_paras.append(p)
    return quiz_paras


def parse_question_blocks(quiz_paras):
    """
    문제 블록 단위로 자르기.
    각 문제는 'N번 (유형)' 으로 시작 → 다음 'N번 (유형)' 직전까지가 한 문제.
    """
    blocks = []
    current = []
    for p in quiz_paras:
        if re.match(r"^\d+번\s*\(", p.strip()):
            if current:
                blocks.append(current)
            current = [p]
        else:
            if current:
                current.append(p)
    if current:
        blocks.append(current)
    return blocks


def parse_one_question(block, topic_id, lesson_no, q_seq):
    """문제 블록 1개 → quiz dict"""
    head = block[0].strip()
    m = re.match(r"^(\d+)번\s*\((.+?)\)", head)
    if not m:
        return None
    num = int(m.group(1))
    style_label = m.group(2).strip()
    # "주관식 – 한 문장" 같은 변형 처리
    style_key = next((k for k in STYLE_MAP if style_label.startswith(k)), None)
    if not style_key:
        return None
    style = STYLE_MAP[style_key]

    # block의 모든 paragraph를 \n 기준으로 line 단위로 평탄화
    raw_lines = []
    for p in block[1:]:
        for ln in p.split("\n"):
            if ln.strip():
                raw_lines.append(ln.strip())

    # '→ 정답:' / '→ 예시 답:' 다음 라인이 '(...)' 단독이면 합쳐서 한 라인으로
    lines = []
    i = 0
    while i < len(raw_lines):
        cur = raw_lines[i]
        if (cur.startswith("→ 정답:") or cur.startswith("→ 예시 답:")) \
           and i + 1 < len(raw_lines) \
           and raw_lines[i + 1].startswith("(") and raw_lines[i + 1].endswith(")"):
            lines.append(cur + " " + raw_lines[i + 1])
            i += 2
        else:
            lines.append(cur)
            i += 1

    question_lines = []
    options = []
    answer_text = ""
    explanation = ""
    bible_ref = ""
    in_options = False

    for s in lines:
        if s.startswith("[보기]"):
            in_options = True
            continue
        if s.startswith("→ 정답:") or s.startswith("→ 예시 답:"):
            ans_part = s.split(":", 1)[1].strip() if ":" in s else ""
            # 괄호 안 해설 분리
            paren_match = re.search(r"\((.+)\)\s*$", ans_part)
            if paren_match:
                explanation_full = paren_match.group(1).strip()
                # 해설 안에서 성경 구절 추출 (괄호 안 또는 끝부분)
                # 패턴 1: "... (딤후 3:16)" 또는 "... (시 119:105)"
                bible_inner = re.search(r"\(([가-힣]+\s*\d+[:\.]\d+(?:[\-\d]+)?)\)\s*$", explanation_full)
                if bible_inner:
                    bible_ref = bible_inner.group(1).strip()
                    explanation = explanation_full[:bible_inner.start()].strip()
                else:
                    # 패턴 2: "... ― 약자 N:N" 또는 "... — 약자 N장 N절"
                    bible_dash = re.search(r"[―—]\s*(.+)$", explanation_full)
                    if bible_dash:
                        bible_ref = bible_dash.group(1).strip()
                        explanation = explanation_full.replace(bible_dash.group(0), "").strip()
                    else:
                        # 패턴 3: 마지막에 "(약자 N장 N절)"
                        bible_kor = re.search(r"\(([가-힣]+\s*\d+장\s*\d+(?:[\-\~\d]*)?절)\)\s*$", explanation_full)
                        if bible_kor:
                            bible_ref = bible_kor.group(1).strip()
                            explanation = explanation_full[:bible_kor.start()].strip()
                        else:
                            explanation = explanation_full
                answer_text = ans_part[:paren_match.start()].strip()
            else:
                answer_text = ans_part
            in_options = False
            continue
        if in_options:
            opt_match = re.match(r"^([①②③④⑤])\s*(.+)$", s)
            if opt_match:
                options.append(opt_match.group(2).strip())
        else:
            question_lines.append(s)

    question = " ".join(question_lines).strip()
    # OX 문제는 question 안에 OX 형식이 들어있고 보기가 없음 → 자동 부여
    if style == "ox" and not options:
        options = ["⭕ 그렇다", "❌ 아니다"]

    # answer_index 계산 (mc/ox/fill만)
    answer_index = None
    if style in ("mc", "ox", "fill") and options and answer_text:
        # 정답 텍스트가 ①~④ 기호인지, 또는 ⭕/❌ 인지, 또는 단어인지
        idx_map = {"①": 0, "②": 1, "③": 2, "④": 3, "⑤": 4}
        if answer_text in idx_map:
            answer_index = idx_map[answer_text]
        elif "⭕" in answer_text or answer_text.startswith("O") or "그렇다" in answer_text:
            answer_index = 0
        elif "❌" in answer_text or answer_text.startswith("X") or "아니다" in answer_text:
            answer_index = 1
        else:
            # 텍스트 매칭
            for i, o in enumerate(options):
                if answer_text in o or o in answer_text:
                    answer_index = i
                    break

    qid = f"q-{topic_id}-{q_seq:02d}"
    quiz = {
        "id": qid,
        "topic_id": topic_id,
        "lesson_no": lesson_no,
        "style": style,
        "question": question,
        "options": options if options else None,
        "answer_index": answer_index,
        "answer_text": answer_text,
        "explanation": explanation,
        "bible_ref": bible_ref,
        "source_origin": "DOCX-자료1",
    }
    # accepted_keywords: open/apply/nonsense는 answer_text 분해
    if style in ("open", "apply"):
        quiz["accepted_keywords"] = []  # 사회자 판단
        quiz["scoring_hint"] = answer_text  # 예시 답
    elif style == "fill":
        # 빈칸 정답은 단어 1개 — accepted_keywords로
        quiz["accepted_keywords"] = [answer_text] if answer_text else []
    elif style in ("mc", "ox"):
        if answer_index is not None and options:
            quiz["accepted_keywords"] = [options[answer_index]]
        else:
            quiz["accepted_keywords"] = []

    return quiz


def main():
    if not SRC.exists():
        print(f"❌ {SRC} not found")
        sys.exit(1)

    d = docx.Document(str(SRC))
    paras = [p.text for p in d.paragraphs]
    print(f"📖 DOCX 로드: {len(paras)} paragraphs")

    lessons = split_into_lessons(paras)
    print(f"📑 과 발견: {[l[0] for l in lessons]}")

    all_quizzes = []
    for lesson_no, lesson_paras in lessons:
        if lesson_no not in TOPIC_MAP:
            print(f"  ⚠️  제{lesson_no}과 → topic_id 매핑 없음 (skip)")
            continue
        topic_id = TOPIC_MAP[lesson_no]
        quiz_paras = extract_quiz_section(lesson_paras)
        blocks = parse_question_blocks(quiz_paras)
        print(f"  📚 제{lesson_no}과 ({topic_id}): {len(blocks)} 문제 블록")

        for q_seq, block in enumerate(blocks, 1):
            quiz = parse_one_question(block, topic_id, lesson_no, q_seq)
            if quiz:
                all_quizzes.append(quiz)
            else:
                print(f"     ❌ block {q_seq} 파싱 실패: {block[0][:60]}")

    # 통계
    by_style = {}
    by_topic = {}
    for q in all_quizzes:
        by_style[q["style"]] = by_style.get(q["style"], 0) + 1
        by_topic[q["topic_id"]] = by_topic.get(q["topic_id"], 0) + 1

    print(f"\n✅ 총 {len(all_quizzes)} 문제 파싱 완료")
    print(f"   by_style: {by_style}")
    print(f"   by_topic: {by_topic}")

    output = {
        "meta": {
            "source": "DOCX 자료1 (교리퀴즈대회 예상문제집)",
            "extracted_at": datetime.now().isoformat(),
            "total": len(all_quizzes),
            "by_style": by_style,
            "by_topic": by_topic,
        },
        "quizzes": all_quizzes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n💾 저장: {OUT}")


if __name__ == "__main__":
    main()
