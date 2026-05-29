import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

export const options = {
  stages: [
    { duration: '15s', target: 10 },
    { duration: '30s', target: 20 },
    { duration: '15s', target: 0 },
  ],
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<500'],
  },
};

function randSuffix() {
  return Math.random().toString(36).slice(2, 10);
}

export default function () {
  // ─ Register fresh user per VU iteration ─────────────
  const u = `user_${__VU}_${__ITER}_${randSuffix()}`;
  const email = `${u}@x.com`;
  const credentials = JSON.stringify({
    username: u,
    email: email,
    password: 'pass123',
  });

  const reg = http.post(`${BASE_URL}/register`, credentials, {
    headers: { 'Content-Type': 'application/json' },
    responseCallback: http.expectedStatuses(201, 400, 409),
  });
  check(reg, { 'register handled': (r) => r.status === 201 || r.status === 400 });

  // ─ Login ───────────────────────────────────────────
  const loginRes = http.post(
    `${BASE_URL}/login`,
    JSON.stringify({ email, password: 'pass123' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(loginRes, { 'login OK': (r) => r.status === 200 });
  if (loginRes.status !== 200) {
    sleep(1);
    return;
  }
  const token = loginRes.json('access_token');
  const authHeaders = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  };

  // ─ Create habit ────────────────────────────────────
  const createRes = http.post(
    `${BASE_URL}/habits`,
    JSON.stringify({ name: 'k6 habit', category: 'fitness', goal_days_per_week: 5 }),
    { headers: authHeaders }
  );
  check(createRes, { 'create habit OK': (r) => r.status === 201 });
  if (createRes.status !== 201) {
    sleep(1);
    return;
  }
  const habitId = createRes.json('id');

  // ─ List habits ─────────────────────────────────────
  const listRes = http.get(`${BASE_URL}/habits`, { headers: authHeaders });
  check(listRes, { 'list habits OK': (r) => r.status === 200 });

  // ─ Track + streak ──────────────────────────────────
  const trackRes = http.post(
    `${BASE_URL}/habits/${habitId}/track`,
    JSON.stringify({ done: true }),
    { headers: authHeaders }
  );
  check(trackRes, { 'track habit OK': (r) => r.status === 201 });

  const streakRes = http.get(`${BASE_URL}/habits/${habitId}/streak`, { headers: authHeaders });
  check(streakRes, { 'streak OK': (r) => r.status === 200 });

  sleep(0.3);
}
