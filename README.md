# 2026 봄 드림아동부 교리퀴즈대회

부모 시스템: **AgenticWorkflow** (`교리퀴즈(시스템)/`)
DNA 유전: 절대 기준 1·2·3 + 4계층 검증 + SOT 패턴

---

## ⚡ 대회 당일 사용법 (가장 중요)

```
1. 노트북에 HDMI 케이블로 TV 연결
2. webapp/index.html 더블클릭
3. [팀전] 또는 [개인전] 선택 → 이름 입력 → ▶ 시작
4. 카드 클릭 → 문제 출제 → 자유 손들기
5. 사회자가 ⭕ 클릭 → 정답 팀 선택 → 마라탕 재료 모달
6. 모든 카드 소진 또는 [🏆 결과 보기] → 시상
```

**인터넷 불필요.** 정전·새로고침해도 자동 복원 (localStorage).

---

## 📊 시스템 사양

| 항목 | 수치 |
|---|---|
| 총 문제 | **100문제** |
| 출처 | 자료1 DOCX 70 + Claude 신규 30 |
| 7과 분포 | 성경 13 · 신 20 · 기독 20 · 성령 12 · 구원 12 · 교회 12 · 종말 11 |
| 7가지 형식 | 객관식 28 · OX 21 · 빈칸 7 · 주관식 7 · 적용 7 · 넌센스 15 · 그림 15 |
| 난이도 | ★ 49 · ★★ 37 · ★★★ 14 |
| 보상 타입 | 🎯 collect 70 · 🔥 steal 15 · 🎁 gift 10 · ♻️ swap 5 |
| 그림 | 15장 (Pollinations.ai 자동 생성) |
| 마라탕 재료 | 12종 |

---

## 🎮 게임 메커니즘

### 모드
- **팀전**: 4팀(빨강/파랑/노랑/초록), 자유 손들기, 팀 인벤토리 합산 1~4위
- **개인전**: 참가자 등록, 자유 손들기, **MVP Top 3 자동 산출**

### 보상 타입 4종
| 🎯 | **collect** | 정답 → 풀에서 재료 1개 선택 |
| 🔥 | **steal**   | 정답 → 다른 팀에서 재료 1개 빼앗기 |
| 🎁 | **gift**    | 정답 → 본인 +2 + 다른 팀에 +1 선물 (순이익 +1, 협력형) |
| ♻️ | **swap**    | 정답 → 다른 팀과 재료 1개 교환 |

### 채점
- OX/객관식/빈칸: 사회자가 정답 토글로 확인
- 주관식/적용/넌센스: 사회자 판단

---

## 🛠 재생성 / 수정

### 부적합 항목 검수 후 재생성

이미지가 신학적·아동 부적합:
```bash
# 해당 png 파일 삭제 후 재실행
rm outputs/images/q-extra-image-05.png
python scripts/04_generate_images.py        # skip 로직으로 누락된 것만 재생성
python scripts/03_build_webapp.py           # 재빌드
```

퀴즈 텍스트 부적합:
```bash
# outputs/quizzes.json을 직접 편집 후
python scripts/03_build_webapp.py
```

전체 재생성 (다른 PDF로 새 대회):
```bash
cp -r ../2026-04-25-doctrine-quiz ../2026-XX-YY-doctrine-quiz
cd ../2026-XX-YY-doctrine-quiz
# 새 source.docx 교체 후
python scripts/01_parse_docx.py     # DOCX 파싱
# (Claude로 신규 30개 생성 — outputs/quizzes-extras.json 갱신)
python scripts/02_assemble.py       # 통합
python scripts/04_generate_images.py # 이미지
python scripts/03_build_webapp.py   # 빌드
```

---

## 📁 폴더 구조

```
2026-04-25-doctrine-quiz/
├── inputs/
│   ├── source.docx              ← 자료1 (예상문제집)
│   ├── teacher.pdf              ← 자료2 (지도자용 — fact-check reference)
│   └── student.pdf              ← 자료3 (학습자용)
├── outputs/
│   ├── quizzes-from-docx.json   ← Phase A3 결과 (70)
│   ├── quizzes-extras.json      ← Phase A5 결과 (30)
│   ├── quizzes.json             ← Phase A6 통합 (100) ⭐
│   └── images/q-extra-image-XX.png  ← Phase C 결과 (15)
├── webapp/                      ← TV 진행용 정적 웹앱 ⭐
│   ├── index.html               (시작)
│   ├── dashboard.html           (카드 대시보드)
│   ├── question.html            (문제 풀이 + 보상 모달)
│   ├── results.html             (마라탕 시상식 + MVP)
│   ├── data.js                  (window.QUIZZES — file:// OK)
│   ├── app.js                   (게임 로직)
│   ├── style.css                (밝은 파스텔)
│   └── images/                  (15 그림)
├── scripts/
│   ├── 01_parse_docx.py         (DOCX → 70문제)
│   ├── 02_assemble.py           (통합 + reward_type)
│   ├── 03_build_webapp.py       (data.js 빌드)
│   ├── 04_generate_images.py    (이미지 생성)
│   └── verify_webapp.py         (smoke test)
├── state.yaml                   (SOT — topics/styles/ingredients/pipeline)
└── README.md                    (이 파일)
```

---

## 🔐 저작권

- `inputs/` 의 PDF·DOCX는 **드림교회 내부 교육용**으로만 사용. 외부 배포 금지.
- 생성된 퀴즈는 본 교회 행사용. 상업 이용 금지.
- 생성 이미지는 Pollinations.ai 라이선스(자유 사용 가능, 사용자 보유)를 따름.

---

## 🧬 부모 시스템(AgenticWorkflow)에서 유전된 DNA

| 부모 게놈 | 자식 발현 |
|---|---|
| 절대 기준 1 (품질) | 100문제 + 4계층 검증 (스키마 + smoke test + 사용자 검수 + /regenerate) |
| 절대 기준 2 (단일 SOT) | 콘텐츠 SOT (`state.yaml`) ↔ 진행 SOT (`localStorage`) 물리 분리 |
| 절대 기준 3 (CCP) | 단계별 Pre/Post-processing, Output 1:1 매핑, 영향 범위 추적 가능 |
| 3단계 구조 | Phase A (Research+Planning 통합) · Phase B (구현) · Phase C (산출 강화) |
| Genome Inheritance | `state.yaml.parent_genome` 메타 |

**상세 설계**: `../../docs/plans/2026-04-25-doctrine-quiz-design.md`
**구현 계획**: `../../docs/plans/2026-04-25-doctrine-quiz-implementation.md`
