# Performans Test Raporu

## Test Ortamı

| Bileşen | Detay |
|---------|-------|
| Araç | k6 v0.50+ |
| Hedef | `http://localhost:8000` (docker-compose) |
| Veritabanı | PostgreSQL 16 |
| CI | GitHub Actions (ubuntu-latest, 2 vCPU, 7 GB RAM) |

## Smoke Test (3 VU · 15s)

`perf/smoke-test.js` — `/health` endpoint'i temel sağlık kontrolü.

| Metrik | Değer | Threshold | Sonuç |
|--------|-------|-----------|-------|
| p(95) latency | ~5 ms | < 300 ms | ✅ |
| Error rate | 0% | < 1% | ✅ |

## Load Test (10→20 VU · 60s)

`perf/load-test.js` — gerçekçi akış: register → login → create habit → list → track → streak.

| Metrik | Değer | Threshold | Sonuç |
|--------|-------|-----------|-------|
| **p(95) latency** | **~285 ms** | < 500 ms | ✅ |
| p(99) latency | ~310 ms | — | ℹ |
| Error rate | 0% | < 5% | ✅ |
| Throughput | ~15 req/s | — | ℹ |

### Endpoint Bazında Gözlemler

| Endpoint | Ort. Latency | Not |
|----------|-------------|-----|
| GET /health | ~2 ms | DB yok, çok hızlı |
| POST /register | ~120 ms | bcrypt password hashing — beklenen |
| POST /login | ~110 ms | bcrypt verify — beklenen |
| POST /habits | ~15 ms | Tek INSERT |
| GET /habits | ~20 ms | Filtered JOIN |
| POST /habits/{id}/track | ~18 ms | UPSERT |
| GET /habits/{id}/streak | ~25 ms | Aggregate query |

## Yorum

- **p(95) = 285 ms** — 500 ms hedefinin çok altında, sistem stabil.
- En yavaş endpoint'ler `/register` ve `/login` — bcrypt hashing güvenlik gereği,
  optimize edilmesi önerilmez.
- 20 eşzamanlı VU altında 0% error rate.

## İleride Yapılabilecekler

- PgBouncer connection pooling → bağlantı overhead azaltmak için.
- Yüksek yükte (50+ VU) backend replicas artırılabilir (`kubectl scale deployment/backend --replicas=4`).
