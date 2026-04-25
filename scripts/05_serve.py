#!/usr/bin/env python3
"""
W1 — Flask 로컬 서버 (자동 저장 인프라)

- GET  /                       : webapp/index.html
- GET  /<path>                 : webapp/<path> (정적)
- GET  /api/session/latest     : outputs/sessions/_current.json
- POST /api/session            : JSON body 저장
                                 → outputs/sessions/_current.json (덮어쓰기 — 빠른 복구용)
                                 → outputs/sessions/<ISO>.json (히스토리, 매 변경마다)

사용법:
  python scripts/05_serve.py
  → http://localhost:8765/
"""
import os, sys, json
from datetime import datetime
from pathlib import Path

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
sys.stdout.reconfigure(encoding="utf-8")

from flask import Flask, request, send_from_directory, jsonify, abort

ROOT = Path(__file__).resolve().parent.parent
WEBAPP = ROOT / "webapp"
SESSIONS = ROOT / "outputs" / "sessions"
SESSIONS.mkdir(parents=True, exist_ok=True)

CURRENT = SESSIONS / "_current.json"
PORT = int(os.environ.get("PORT", "8765"))

app = Flask(__name__, static_folder=str(WEBAPP), static_url_path="")


# ─── Static webapp ───────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(WEBAPP), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    fp = WEBAPP / filename
    if not fp.exists():
        abort(404)
    return send_from_directory(str(WEBAPP), filename)


# ─── Session API ─────────────────────────────────────────
@app.route("/api/session/latest", methods=["GET"])
def get_latest():
    if not CURRENT.exists():
        return jsonify(None)
    try:
        data = json.loads(CURRENT.read_text(encoding="utf-8"))
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/session", methods=["POST"])
def save_session():
    try:
        data = request.get_json(force=True)
        if not isinstance(data, dict):
            return jsonify({"error": "invalid body"}), 400

        # 1) 빠른 복구용 — 항상 같은 파일 덮어쓰기
        CURRENT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        # 2) 히스토리 — 타임스탬프 파일 (매 변경마다 누적)
        ts = datetime.now().strftime("%Y-%m-%dT%H-%M-%S-%f")[:-3]
        history = SESSIONS / f"{ts}.json"
        history.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        return jsonify({"ok": True, "saved_at": ts})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/session", methods=["DELETE"])
def clear_session():
    """대회 종료/리셋 시 _current 만 삭제 (히스토리는 보존)"""
    if CURRENT.exists():
        CURRENT.unlink()
    return jsonify({"ok": True})


# ─── 헬스체크 ────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "webapp_exists": WEBAPP.exists(),
        "sessions_dir": str(SESSIONS),
        "current_exists": CURRENT.exists(),
        "history_count": len(list(SESSIONS.glob("*.json"))) - (1 if CURRENT.exists() else 0),
    })


if __name__ == "__main__":
    print(f"📡 Serving webapp at http://localhost:{PORT}/")
    print(f"💾 Sessions auto-saved to: {SESSIONS}")
    print(f"   - _current.json (빠른 복구용)")
    print(f"   - <timestamp>.json (히스토리)")
    print(f"\n   Ctrl+C to stop\n")
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)
