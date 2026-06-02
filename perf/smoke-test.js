import http from 'k6/http';
import { check, sleep } from 'k6';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// SMOKE = "ayakta mı?" doğrulaması — YÜK testi değil.
// Her iterasyonda sleep(1) var; bu yüzden /health'i saniyede ~1-2 istekle
// nazikçe yoklar (eski hali sleep'siz 3 VU ile ~960 req/s üretiyordu →
// Grafana'da /health'in fırlamasının sebebi buydu). Yük testi: load-test.js
export const options = {
  vus: 2,
  duration: '10s',
  thresholds: {
    http_req_failed: ['rate<0.01'],
    http_req_duration: ['p(95)<300'],
  },
};

export default function () {
  const r = http.get(`${BASE_URL}/health`);
  check(r, { 'health 200': (res) => res.status === 200 });
  sleep(1);
}
