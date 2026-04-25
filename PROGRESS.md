# 드림아동부 교리퀴즈 시스템 — 진행 상황 (2026-04-25 저장)

> 다음 세션에서 이어서 진행할 때 이 문서부터 읽으세요.

---

## 1. 시스템 현재 상태

### ✅ 완료된 산출물

| 영역 | 상태 | 위치 |
|---|---|---|
| **콘텐츠 데이터** | 100문제 완성 | `outputs/quizzes.json` |
| **이미지** | 15장 생성 (Pollinations.ai) | `outputs/images/` + `webapp/images/` |
| **웹앱 통합 SPA** | 1개 URL로 전 기능 | `webapp/index.html` (단일 파일) |
| **백엔드** | Flask 자동 저장 서버 | `scripts/05_serve.py` (포트 8765) |
| **자동 저장** | 매 정답 처리마다 폴더 저장 | `outputs/sessions/_current.json` + 히스토리 |
| **부모-자식 분리** | DNA 유전 패턴 | `state.yaml.parent_genome` |

### 📂 핵심 파일 인벤토리

```
children/2026-04-25-doctrine-quiz/
├── PROGRESS.md                  ← 이 문서 (재개 진입점)
├── README.md                    (사용법)
├── state.yaml                   (SOT)
├── workflow.md                  (4단계 워크플로우)
│
├── inputs/
│   ├── source.docx              (자료1 — 원본 보존)
│   ├── teacher.pdf              (자료2)
│   └── student.pdf              (자료3)
│
├── outputs/
│   ├── quizzes.json             (마스터 100문제) ⭐
│   ├── quizzes-from-docx.json   (DOCX 70문제)
│   ├── quizzes-extras.json      (신규 30문제)
│   ├── images/q-extra-image-XX.png  (15장)
│   └── sessions/                (대회 진행 자동 저장)
│       ├── _current.json        (최신 — 빠른 복구)
│       └── <ISO>.json (히스토리)
│
├── webapp/                      (TV 진행용 정적 + Flask)
│   ├── index.html               ⭐ 통합 SPA (모든 기능 한 파일)
│   ├── dashboard.html           (백업 — 옛 분리 버전)
│   ├── question.html            (백업)
│   ├── results.html             (백업)
│   ├── data.js                  (window.QUIZZES 인라인)
│   ├── app.js                   (게임 로직 + saveSession 이중화)
│   ├── style.css                (다크 navy + sky blue, Pretendard Variable)
│   └── images/                  (15장 복사본)
│
└── scripts/
    ├── 01_parse_docx.py         (DOCX → 70문제)
    ├── 02_assemble.py           (통합 + difficulty + reward_type)
    ├── 03_build_webapp.py       (data.js 빌드)
    ├── 04_generate_images.py    (Pollinations 이미지 생성)
    ├── 05_serve.py              ⭐ Flask 서버 (자동 저장 API)
    └── verify_webapp.py         (smoke test)
```

---

## 2. 100문제 분포 (확정)

| 항목 | 값 |
|---|---|
| 총 문제 | 100 (DOCX 70 + 신규 30) |
| 7과 분포 | 성경 13 · 신 20 · 기독 20 · 성령 12 · 구원 12 · 교회 12 · 종말 11 |
| 7가지 형식 | 객관식 28 · OX 21 · 빈칸 7 · 주관식 7 · 적용 7 · 넌센스 15 · 그림 15 |
| 난이도 | ★ 49 · ★★ 37 · ★★★ 14 |
| 보상 타입 | 🎯 collect 70 · 🔥 steal 15 · 🎁 gift 10 · ♻️ swap 5 |

---

## 3. 핵심 결정 사항 (확정)

| # | 결정 | 사용자 확정 시점 |
|---|---|---|
| 1 | 자식 시스템 분리 (`children/.../`) | 초기 안 2 승인 |
| 2 | 100문제 분량 + 7과 + 7형식 + 4 reward | A6 통합 시점 |
| 3 | 게임 메커니즘: 마라탕 재료 인벤토리 | 마라탕 추가 시점 |
| 4 | 팀전 + 개인전 + MVP Top 3 | 세 번째 질문 답 |
| 5 | 자유 손들기 룰 | 4팀 진행 룰 결정 |
| 6 | 디자인: 다크 navy + Sky blue (Summer-Revival-LMS DNA) | Summer-Revival-LMS 참고 후 |
| 7 | 단일 통합 SPA (`/`) | "통합 대시보드" 요청 |
| 8 | 자동 저장 = Flask 백엔드 (옵션 A) | 수정 계획 v1 승인 |
| 9 | 5단계 문제 풀이 흐름 | 5단계 흐름 승인 |
| 10 | 대회 날짜 2026-04-26 | "드림아동부 / 4월 26일" 요청 |

---

## 4. 미결 사항 — 다음 세션에서 결정 필요

### 🔴 가장 시급 — 수정 계획 v2 (M1~M8) 적용 승인 대기

**가독성 + 디자인 + 기능 균형 원칙으로 8개 수정 단위 설계됨**:

| # | 변경 | 가독성 | 디자인 | 기능 |
|---|---|---|---|---|
| M1 | 정답 확인란 평소 숨김 + 우상단 🔒 버튼 + `A` 단축키 (1.5초 표시 후 자동 닫힘) | ✅ | ✅ | ✅ |
| M2 | 마라탕 reward 모달 단순화 — 재료 종류 그리드 제거, 큰 문구만 | ✅ | ✅ | 부분 (재료 종류 무시) |
| M3 | 점수판 — 큰 숫자만 (이모지 제거) | ✅ | ✅ | ✅ |
| M4 | 보기 자동 채점 — Step 3에서만 + 1.5초 자동 페이드 | ✅ | ✅ | ✅ |
| M5 | 정답 처리 후 큰 토스트 (예: "🎉 빨강팀 정답! 🍲 +1") | ✅ | ✅ | ✅ |
| M6 | swap reward type 새 의미 — **양 팀 +1 (협력 보너스)** | ✅ | ✅ | ✅ |
| M7 | 인벤토리 시스템 호환성 유지 (배열 + length) | — | — | ✅ |
| M8 | TV 가독성 강화 — 카드 폰트·점수 폰트·토스트 폰트 키움 | ✅ | ✅ | — |

**남은 결정**: swap 처리 — (a) 양 팀 +1 협력 ⭐ / (b) collect 흡수 / (c) 재료 종류 유지

### 🟡 추후 고려 사항

- 실제 대회 진행 시 사회자 핸드폰 보조 화면 필요 여부 (옵션 Y)
- 듀얼 모니터 환경 지원 (옵션 Z)
- 결과 저장 — 대회 종료 후 자동 PDF 출력?
- 다음 PDF로 새 대회 만들 때 재사용 패턴 검증

---

## 5. 알려진 이슈 / 모순

| 이슈 | 상태 |
|---|---|
| 정답 확인란이 TV에 노출됨 | M1으로 해결 예정 |
| 보기 클릭 자동 채점이 모든 단계에서 작동 | M4로 해결 예정 |
| 점수판 재료 이모지가 실물 재료와 분리되어 무의미 | M3으로 해결 예정 |
| swap 메커니즘이 재료 종류 제거 시 무의미 | M6으로 새 의미 부여 |

---

## 6. 시스템 실행 방법

### 대회 당일 (사용자 작업)

```bash
# 1. Flask 서버 실행 (포트 8765)
cd children/2026-04-25-doctrine-quiz
python scripts/05_serve.py

# 2. 브라우저 접속 (TV에 표시)
http://localhost:8765/
```

### 콘텐츠 재생성 (PDF 변경 시)

```bash
python scripts/01_parse_docx.py     # DOCX → 70문제
# (Claude로 신규 30개 생성 — outputs/quizzes-extras.json)
python scripts/02_assemble.py       # 통합 100
python scripts/04_generate_images.py # 이미지 (Pollinations)
python scripts/03_build_webapp.py   # data.js 빌드
python scripts/verify_webapp.py     # smoke test
```

---

## 7. 다음 세션 진입 가이드

### 즉시 재개 가능한 작업

1. **수정 계획 v2 (M1~M8) 일괄 적용** — 사용자 승인 후 30분 내 완료
   - 변경 파일: `webapp/index.html` + `webapp/style.css` 단 2개
   - swap 처리 결정만 받으면 즉시 시작

2. **사용자 검수 + 피드백 반복** — 대회 전 1주일

### 작업 시작 전 확인할 것

```bash
# 1. Flask 서버가 살아있는지
curl http://localhost:8765/api/health

# 2. quizzes.json 무결성
python -c "import json; d=json.load(open('children/2026-04-25-doctrine-quiz/outputs/quizzes.json',encoding='utf-8')); print('total:', d['meta']['total'])"

# 3. 자동 저장본 존재 여부
ls children/2026-04-25-doctrine-quiz/outputs/sessions/
```

---

## 8. 참조 문서 (이 시스템 외)

| 문서 | 위치 |
|---|---|
| 부모 시스템 헌법 | `../../CLAUDE.md` (상위 폴더) |
| AGENTS.md (방법론 SOT) | `../../AGENTS.md` |
| soul.md §0 (DNA 유전 정의) | `../../soul.md` |
| 설계 문서 | `../../docs/plans/2026-04-25-doctrine-quiz-design.md` |
| 구현 계획서 | `../../docs/plans/2026-04-25-doctrine-quiz-implementation.md` |
| 자료1 DOCX 원본 | `inputs/source.docx` |
| 참고 디자인 | `C:/Users/yijae/Desktop/Summer-Revival-LMS/` (Next.js 풀스택 LMS) |

---

**작성**: 2026-04-25 (이 세션 종료 시점)
**다음 단계**: 사용자가 수정 계획 v2 (M1~M8) 승인 후 일괄 적용
