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

// k6 her VU'yu ayrı JS örneğinde çalıştırır → modül seviyesi değişkenler
// VU'ya özeldir. Her VU kullanıcısını BİR KEZ kurar, sonra token'ı yeniden
// kullanır. (Gerçek kullanıcı her istekte kayıt olmaz; bu, bcrypt'in her
// iterasyonda CPU'yu doyurmasını engeller → gerçekçi yük profili.)
let authHeaders = null;
let habitId = null;

function setupUser() {
  const email = `loaduser_${__VU}@x.com`;
  const json = { 'Content-Type': 'application/json' };
  http.post(
    `${BASE_URL}/register`,
    JSON.stringify({ username: `loaduser_${__VU}`, email, password: 'pass123' }),
    { headers: json, responseCallback: http.expectedStatuses(201, 400, 409) }
  );
  const login = http.post(
    `${BASE_URL}/login`,
    JSON.stringify({ email, password: 'pass123' }),
    { headers: json }
  );
  check(login, { 'login OK': (r) => r.status === 200 });
  if (login.status !== 200) return false;
  authHeaders = { 'Content-Type': 'application/json', Authorization: `Bearer ${login.json('access_token')}` };

  const create = http.post(
    `${BASE_URL}/habits`,
    JSON.stringify({ name: 'k6 habit', category: 'fitness', goal_days_per_week: 5 }),
    { headers: authHeaders }
  );
  check(create, { 'create habit OK': (r) => r.status === 201 });
  if (create.status === 201) habitId = create.json('id');
  return true;
}

export default function () {
  // İlk iterasyonda kullanıcı + habit kur (VU başına bir kez)
  if (!authHeaders) {
    if (!setupUser()) { sleep(1); return; }
  }

  // ─ Gerçek kullanım: ucuz authenticated istekler ─────
  const list = http.get(`${BASE_URL}/habits`, { headers: authHeaders });
  check(list, { 'list habits OK': (r) => r.status === 200 });

  if (habitId) {
    const track = http.post(
      `${BASE_URL}/habits/${habitId}/track`,
      JSON.stringify({ done: true }),
      { headers: authHeaders }
    );
    check(track, { 'track OK': (r) => r.status === 201 });

    const streak = http.get(`${BASE_URL}/habits/${habitId}/streak`, { headers: authHeaders });
    check(streak, { 'streak OK': (r) => r.status === 200 });
  }

  sleep(1);
}
