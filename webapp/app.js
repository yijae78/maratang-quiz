// 아동부 교리퀴즈 — 게임 로직 + localStorage
// 의존: data.js (window.QUIZZES = {meta, quizzes, ingredients, topics, styles, reward_types})

const STORAGE_KEY = 'doctrine_quiz_session';

const TEAM_COLORS = ['red', 'blue', 'yellow', 'green'];

// ═════════ 미션 카드 5장 (관리자 비밀번호로 미리보기) ═════════
const ADMIN_PASS_DEFAULT = '1004';
const ADMIN_PASS_KEY = 'admin_pass';
function getAdminPass() {
  return localStorage.getItem(ADMIN_PASS_KEY) || ADMIN_PASS_DEFAULT;
}
function setAdminPass(newPass) {
  if (newPass && newPass.length >= 4) {
    localStorage.setItem(ADMIN_PASS_KEY, newPass);
    return true;
  }
  return false;
}
const MISSION_CARDS = [
  { id: 'm-001', is_mission: true, style: 'mission', difficulty: 1, reward_type: 'collect', mission_emoji: '🙌', mission_title: '협동 미션', mission_text: '팀원 모두 일어서서 만세 3번 외치기!', mission_seconds: 20 },
  { id: 'm-002', is_mission: true, style: 'mission', difficulty: 1, reward_type: 'collect', mission_emoji: '🎵', mission_title: '찬양 미션', mission_text: '팀원 한 명이 찬양 한 소절 부르기', mission_seconds: 20 },
  { id: 'm-003', is_mission: true, style: 'mission', difficulty: 1, reward_type: 'collect', mission_emoji: '✋', mission_title: '하이파이브 미션', mission_text: '팀원 한 명이 선생님 한 분에게 가서 하이파이브하고 오기!', mission_seconds: 20 },
  { id: 'm-004', is_mission: true, style: 'mission', difficulty: 1, reward_type: 'collect', mission_emoji: '🤗', mission_title: '포옹 미션', mission_text: '팀원 한 명이 선생님 한 분에게 가서 꼭 안아드리고 오기!', mission_seconds: 20 },
  { id: 'm-005', is_mission: true, style: 'mission', difficulty: 1, reward_type: 'collect', mission_emoji: '🤝', mission_title: '칭찬 미션', mission_text: '옆 팀원의 칭찬 5가지 말하기', mission_seconds: 20 },
];

// ─── Session State ────────────────────────────────────
function loadSession() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;
  try { return JSON.parse(raw); } catch { return null; }
}
function saveSession(s) {
  // 1) localStorage 즉시 저장 (현행)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
  // 2) 서버 비동기 POST (Flask 서버 동작 시) — 한쪽 실패해도 다른 쪽은 안전
  try {
    fetch('/api/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(s),
    }).catch(() => {});  // 서버 다운돼도 무시
  } catch {}
}
function clearSession() {
  localStorage.removeItem(STORAGE_KEY);
  try { fetch('/api/session', { method: 'DELETE' }).catch(() => {}); } catch {}
}

// 서버에서 가장 최근 세션 가져오기 (반환: Promise<session|null>)
async function fetchServerSession() {
  try {
    const r = await fetch('/api/session/latest');
    if (!r.ok) return null;
    const data = await r.json();
    return (data && typeof data === 'object' && data.mode) ? data : null;
  } catch {
    return null;
  }
}

// localStorage와 서버 둘 다 확인하여 더 최신을 채택
async function loadSessionWithServerSync() {
  const local = loadSession();
  const server = await fetchServerSession();
  if (!local && !server) return null;
  if (local && !server) return local;
  if (!local && server) {
    // 서버에만 있으면 localStorage에도 복원 (다음 로드 빠르게)
    localStorage.setItem(STORAGE_KEY, JSON.stringify(server));
    return server;
  }
  // 둘 다 있으면 started_at 비교 후 더 최신 (실은 같은 세션이므로 보통 같음, 다르면 서버 우선)
  const lt = new Date(local.started_at || 0).getTime();
  const st = new Date(server.started_at || 0).getTime();
  if (st > lt) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(server));
    return server;
  }
  return local;
}

function newSession(mode, names) {
  const session = {
    mode,
    started_at: new Date().toISOString(),
    solved: [],
    current_quiz_id: null,
  };
  if (mode === 'team') {
    session.teams = names.map((name, i) => ({
      name, color: TEAM_COLORS[i] || 'red', inventory: []
    }));
  } else {
    session.players = names.map(name => ({ name, inventory: [] }));
  }
  saveSession(session);
  return session;
}

// ─── Lookups ──────────────────────────────────────────
function getQuiz(id) { return window.QUIZZES.quizzes.find(q => q.id === id); }
function getIngredient(id) { return window.QUIZZES.ingredients.find(i => i.id === id); }
function getTopic(id) { return window.QUIZZES.topics.find(t => t.id === id); }
function emojiOf(ingId) { const i = getIngredient(ingId); return i ? i.emoji : '?'; }
function actorsOf(s) { return s.mode === 'team' ? s.teams : s.players; }

// ─── Render Common ────────────────────────────────────
function renderScorePanel(session) {
  const actors = actorsOf(session);
  const cls = session.mode === 'individual' ? 'individual' : '';
  const html = actors.map(a => {
    const colorClass = a.color || 'individual';
    return `
      <div class="team-card ${colorClass}">
        <div class="team-name">${escapeHtml(a.name)}</div>
        <div class="team-score">${a.inventory.length}</div>
      </div>
    `;
  }).join('');
  return `<div class="score-panel ${cls}">${html}</div>`;
}

function renderCardGrid(session, filter = {}) {
  // 원본 인덱스 기반 통일 번호 (필터 적용해도 번호 고정)
  const STYLE_LABEL = { mc:'객관식', ox:'OX', fill:'빈칸', open:'주관식', apply:'적용', nonsense:'넌센스', image:'그림', mission:'🎁 미션' };
  return window.QUIZZES.quizzes
    .map((q, idx) => ({ q, no: idx + 1 }))
    .filter(({q}) => {
      if (filter.difficulty && q.difficulty !== filter.difficulty) return false;
      if (filter.style && q.style !== filter.style) return false;
      if (filter.topic && q.topic_id !== filter.topic) return false;
      return true;
    })
    .map(({q, no}) => {
      const solved = session.solved.includes(q.id);
      const label = STYLE_LABEL[q.style] || q.style;
      const diff = q.difficulty || 1;
      const isMission = q.is_mission;
      const topic = q.topic_id ? getTopic(q.topic_id) : null;
      const topicColor = topic && topic.color ? topic.color : '#64748b';
      const topicStyle = `style="border-bottom-color: ${topicColor};"`;
      // reward 이모티콘 제거 (#118) — 카드는 번호+카테고리만
      return `
        <div class="quiz-card style-${q.style} diff-${diff} ${solved ? 'solved' : ''} ${isMission ? 'mission-card' : ''}"
             ${topicStyle}
             ${solved ? '' : `onclick="goToQuestion('${q.id}')"`}>
          <div class="card-no">${isMission ? '🎁' : no}</div>
          <div class="card-cat">${label}</div>
        </div>
      `;
    }).join('');
}

// ─── Navigation ───────────────────────────────────────
function goToQuestion(quizId) {
  const s = loadSession();
  if (!s) { goToHome(); return; }
  s.current_quiz_id = quizId;
  saveSession(s);
  window.location.href = 'question.html';
}
function goToDashboard() { window.location.href = 'dashboard.html'; }
function goToResults()   { window.location.href = 'results.html'; }
function goToHome()      { window.location.href = 'index.html'; }

// ─── Reward Logic ─────────────────────────────────────
function applyReward(quizId, winnerIdx, opts) {
  const s = loadSession();
  const quiz = getQuiz(quizId);
  const actors = actorsOf(s);
  const winner = actors[winnerIdx];

  switch (quiz.reward_type) {
    case 'collect':
      winner.inventory.push(opts.ingredient_id);
      break;
    case 'steal': {
      const target = actors[opts.target_idx];
      const ix = target.inventory.indexOf(opts.ingredient_id);
      if (ix !== -1) {
        target.inventory.splice(ix, 1);
        winner.inventory.push(opts.ingredient_id);
      }
      break;
    }
    case 'gift': {
      // 본인 +2 (풀에서)
      winner.inventory.push(opts.collect_1, opts.collect_2);
      // 다른 팀에 1개 선물 (본인 인벤토리에서 차감)
      const target = actors[opts.target_idx];
      const myIx = winner.inventory.indexOf(opts.gift_id);
      if (myIx !== -1) {
        winner.inventory.splice(myIx, 1);
      }
      target.inventory.push(opts.gift_id);
      break;
    }
    case 'swap': {
      // 양 팀 +1 협력 보너스 (재료 종류 X — 실물 분배)
      const target = actors[opts.target_idx];
      winner.inventory.push(null);
      target.inventory.push(null);
      break;
    }
  }

  s.solved.push(quizId);
  s.current_quiz_id = null;
  saveSession(s);
}

// 정답인데 선택된 사람·팀 없이 패스
function markSkipped(quizId) {
  const s = loadSession();
  s.solved.push(quizId);
  s.current_quiz_id = null;
  saveSession(s);
}

// ─── Ranking ──────────────────────────────────────────
function computeRanking() {
  const s = loadSession();
  const actors = actorsOf(s);
  return actors
    .map(a => ({
      ...a,
      total: a.inventory.length,
      diversity: new Set(a.inventory).size,
    }))
    .sort((x, y) => y.total - x.total || y.diversity - x.diversity);
}

// ─── HTML escape ──────────────────────────────────────
function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
