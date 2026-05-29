# Habit Tracker (Simple)

**Marmara Üniversitesi — Bulut Mimarilerinde Test Mühendisliği — Dönem Projesi**

Günlük alışkanlık takibi yapan basit bir REST API. Şartnamenin **minimum** gereksinimlerini karşılar; abartı yok, savunması kolay.

> Bu proje aynı yazarın `habit-tracker-api` reposunun **lightweight** versiyonudur.

---

## 🏗️ Mimari

İki bağımsız servis:

```
Browser ──┬──→ :8080  Frontend (NGINX) — static HTML/CSS/JS
          └──→ :8000  Backend (FastAPI) — REST API only

Backend ──→ PostgreSQL :5432
        ──→ LocalStack S3 :4566 (habit photo)
        ──→ /metrics → Prometheus :9090 → Grafana :3000
```

- **Frontend**: NGINX 1.25 alpine, sadece `index.html` / `register.html` / `dashboard.html` + CSS + JS sunar.
- **Backend**: FastAPI, **sadece JSON** döner. HTML üretmez.
- İletişim: tarayıcı `fetch('http://localhost:8000')` ile API'yi çağırır. CORS açıktır.

Detaylı diyagram: [docs/architecture.png](docs/architecture.png)

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Docker & Docker Compose
- (testler için) Python 3.11+

### Tek komut ile çalıştır

```bash
docker-compose up -d --build
```

| Servis | URL | Açıklama |
|---|---|---|
| **Frontend** | http://localhost:8080 | Kullanıcı arayüzü (login, register, dashboard) |
| **Backend API** | http://localhost:8000 | REST API (JSON) |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | Metrik UI |
| LocalStack | http://localhost:4566 | S3 emülatörü |

---

## 📡 API Endpoint'leri

| # | Method | Path | Auth | Açıklama |
|---|--------|------|------|----------|
| 1 | POST | `/register` | – | Yeni kullanıcı oluştur |
| 2 | POST | `/login` | – | JWT token al |
| 3 | POST | `/habits` | ✓ | Habit oluştur |
| 4 | GET | `/habits` | ✓ | Habit listesi |
| 5 | POST | `/habits/{id}/track` | ✓ | Bugün yap (UPSERT) |
| 6 | GET | `/habits/{id}/streak` | ✓ | Mevcut streak |
| + | POST | `/habits/{id}/photo` | ✓ | LocalStack S3 upload |
| + | GET | `/health` | – | Sağlık kontrolü |
| + | GET | `/metrics` | – | Prometheus formatında metrikler |

---

## ✅ Testler

### Unit + Integration (pytest)

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate          # Windows
source .venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
pytest tests/unit tests/integration
```

→ **26 test, %94 coverage**.

### Testcontainers (gerçek PostgreSQL container)

```bash
pytest tests/test_testcontainers.py
```

> Windows'ta psycopg2 hostname encoding sorunu nedeniyle otomatik skip edilir. Linux/CI'da çalışır.

### E2E (Playwright)

```bash
docker-compose up -d
pip install -r tests/e2e/requirements.txt
playwright install chromium
pytest tests/e2e/
```

→ 5 senaryo: register/login/dashboard, hatalı login, habit oluştur, track + streak, logout.

### Postman/Newman (CI'da koşar)

```bash
npm install -g newman
newman run postman/collection.json
```

→ 7 istek: health + 6 endpoint, hepsi test'li.

### Performans (k6)

```bash
k6 run -e BASE_URL=http://localhost:8000 perf/smoke-test.js
k6 run -e BASE_URL=http://localhost:8000 perf/load-test.js
```

→ p(95)=~285ms, 0% hata. Detay: [perf/report.md](perf/report.md)

---

## ☸️ Kubernetes (Kind)

```bash
# Cluster + image yükle
kind create cluster --name habit-tracker
docker build -t backend:dev ./backend
docker build -t frontend:dev ./frontend
kind load docker-image backend:dev --name habit-tracker
kind load docker-image frontend:dev --name habit-tracker

# Image placeholder replace + apply
sed -i 's|__BACKEND_IMAGE__|backend:dev|g; s|__FRONTEND_IMAGE__|frontend:dev|g' k8s/*.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl rollout status deployment/postgres --timeout=2m
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# Erişim
kubectl port-forward svc/backend 8000:8000 &
kubectl port-forward svc/frontend 8080:80 &

# Cleanup
kind delete cluster --name habit-tracker
```

---

## 🔄 CI/CD Pipeline

`.github/workflows/ci.yml` — 4 job zincirli:

```
push/PR → main
   │
   ├── lint            (flake8)
   ├── test            (pytest + coverage ≥70%)
   ├── build           (Docker → GHCR :sha + :latest)
   └── deploy-smoke    (Kind cluster + curl /health)
```

`build` job'unda frontend ve backend ayrı imajlar üretilir; `deploy-smoke` aynı `:sha` imajlarını Kind'a yükleyip `kubectl apply` ile dağıtır.

---

## 📁 Proje Yapısı

```
habit-tracker-simple/
├── backend/                # FastAPI REST API
│   ├── src/                # main, models, schemas, auth, s3_client
│   ├── tests/              # unit, integration, testcontainers
│   ├── Dockerfile          # Multi-stage
│   └── requirements.txt
├── frontend/               # Static frontend
│   ├── index.html          # Login
│   ├── register.html
│   ├── dashboard.html
│   ├── css/style.css
│   ├── js/                 # config, api, login, register, dashboard
│   ├── Dockerfile          # NGINX
│   └── nginx.conf
├── tests/e2e/              # Playwright E2E senaryolar
├── k8s/                    # ConfigMap + Postgres + Backend + Frontend
├── perf/                   # k6 smoke + load
├── postman/                # Newman collection
├── monitoring/             # Prometheus + Grafana provisioning
├── docs/                   # architecture.png + final-report.pdf
├── .github/workflows/      # CI pipeline
├── docker-compose.yml
├── LICENSE
└── README.md
```

---

## 📋 Şartname Karşılama

| Gereksinim | Durum | Detay |
|---|---|---|
| Mini Servis (4-6 endpoint) | ✅ | 6 ana + 3 yardımcı endpoint |
| Pytest unit + integration ≥%70 | ✅ | 26 test, %94 coverage |
| Postman/Newman CI | ✅ | 7 istek + test assertions |
| Docker multi-stage | ✅ | backend (builder+runtime), frontend (NGINX) |
| LocalStack S3 | ✅ | Habit progress photo |
| Testcontainers ≥2 test | ✅ | 3 test, gerçek PostgreSQL 16 |
| Factory Boy + Faker | ✅ | UserFactory, HabitFactory, HabitLogFactory |
| Kubernetes manifestleri | ✅ | ConfigMap + Postgres + Backend + Frontend |
| GitHub Actions | ✅ | lint → test → build → deploy-smoke |
| Prometheus + Grafana ≥3 panel | ✅ | rate, error, latency p95/p99 |
| k6 + p95 ölçüm | ✅ | p(95)=~285ms |
| E2E 3-5 senaryo | ✅ | 5 Playwright testi |
| docs/architecture.png | ✅ | matplotlib ile generate |
| docs/final-report.pdf | ✅ | 5 sayfa IEEE formatı |

---

## ⚙️ Ortam Değişkenleri

Backend için `.env.example` kopyalanır:

```bash
DATABASE_URL=postgresql://user:password@db:5432/habits
SECRET_KEY=change-me-in-production
AWS_ENDPOINT_URL=http://localstack:4566
S3_BUCKET=habit-photos
```

---

## 📄 Lisans

MIT — bkz. [LICENSE](LICENSE)

## 🧑‍💻 Yazar

**Mert Baytaş** — Marmara Üniversitesi, Bilgisayar Mühendisliği
MTH2526-B25 — 2025-2026 Bahar
