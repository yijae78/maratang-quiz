#!/usr/bin/env python3
"""
C1 — 이미지 생성
- 그림 문제(style=image)의 image_concept를 prompt로 사용
- 폴백 체인: Gemini CLI (있으면) → Pollinations.ai (무인증 무료)
- 결과 → outputs/images/<quiz_id>.webp  (또는 .png)
"""
import os, sys, json, shutil, subprocess, urllib.request, urllib.parse, time
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
QUIZZES = ROOT / "outputs" / "quizzes.json"
IMAGES = ROOT / "outputs" / "images"

STYLE_SUFFIX = ", warm cartoon, soft pastel colors, friendly child-friendly art, korean christian kids book illustration, soft lighting, no text, no caption"
NEGATIVE = "photorealistic, scary, dark, gore, weapon, blood, jesus face close-up, god face, religious icon realistic, creepy"


def try_gemini_cli(prompt: str, out_path: Path) -> bool:
    """Gemini CLI (Imagen) — 설치돼 있으면 사용"""
    if not shutil.which("gemini"):
        return False
    try:
        r = subprocess.run(
            ["gemini", "image", "--prompt", prompt + STYLE_SUFFIX,
             "--negative-prompt", NEGATIVE, "--output", str(out_path)],
            capture_output=True, text=True, timeout=120
        )
        return r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 5000
    except Exception:
        return False


def try_pollinations(prompt: str, out_path: Path) -> bool:
    """Pollinations.ai — 무인증 무료"""
    full = prompt + STYLE_SUFFIX
    encoded = urllib.parse.quote(full)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=768&nologo=true&seed={hash(prompt) % 1000000}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            data = r.read()
        if len(data) < 5000:
            return False
        out_path.write_bytes(data)
        return True
    except Exception as e:
        print(f"     Pollinations error: {type(e).__name__}: {str(e)[:80]}")
        return False


def generate_one(quiz: dict) -> tuple[bool, str]:
    qid = quiz["id"]
    concept = quiz.get("image_concept") or quiz.get("question", "")
    out_path = IMAGES / f"{qid}.png"  # Pollinations는 png 반환

    print(f"  [{qid}] {concept[:60]}...")

    if try_gemini_cli(concept, out_path):
        return True, "Gemini"
    if try_pollinations(concept, out_path):
        return True, "Pollinations"
    return False, "all-failed"


def main():
    if not QUIZZES.exists():
        print(f"❌ {QUIZZES} not found"); sys.exit(1)

    data = json.loads(QUIZZES.read_text(encoding="utf-8"))
    image_quizzes = [q for q in data["quizzes"] if q.get("style") == "image"]
    print(f"📷 그림 문제 {len(image_quizzes)}개 처리 시작\n")
    IMAGES.mkdir(parents=True, exist_ok=True)

    results = []
    success = 0
    for i, q in enumerate(image_quizzes, 1):
        # 이미 이미지가 있으면 skip (재실행 시간 절약)
        existing = list(IMAGES.glob(f"{q['id']}.*"))
        if existing and existing[0].stat().st_size > 5000:
            print(f"  [{q['id']}] ✓ 이미 존재 (skip)")
            results.append((q['id'], True, "cached"))
            success += 1
            continue

        ok, src = generate_one(q)
        results.append((q['id'], ok, src))
        if ok:
            size = (IMAGES / f"{q['id']}.png").stat().st_size
            print(f"     ✅ ({src}, {size:,} bytes)")
            success += 1
        else:
            print(f"     ❌ all fallbacks failed")
        time.sleep(0.5)  # rate limit 친화적

    print(f"\n📊 결과: {success}/{len(image_quizzes)} 성공")
    for qid, ok, src in results:
        print(f"   {('✅' if ok else '❌')} {qid} ({src})")

    failed = [r[0] for r in results if not r[1]]
    if failed:
        print(f"\n⚠️  실패 {len(failed)}개 — webapp에서 텍스트 문제로 동작")
        print(f"   재시도: python scripts/04_generate_images.py")

    print(f"\n💡 다음: python scripts/03_build_webapp.py (이미지 포함 재빌드)")


if __name__ == "__main__":
    main()
