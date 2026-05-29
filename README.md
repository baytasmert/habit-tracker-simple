# Habit Tracker (Simple)

**Marmara Üniversitesi — Bulut Mimarilerinde Test Mühendisliği — Dönem Projesi**

Günlük alışkanlık takibi yapan minimal bir REST API. Şartnamenin **tüm** gereksinimlerini + **2 bonus (Jaeger +5, ArgoCD +5)** karşılar. Abartı yok, savunulması kolay.

> Bu proje, aynı yazarın `habit-tracker-api` reposunun **lightweight** versiyonudur.

---

## 🏗️ Mimari

```
Browser ──┬──→ :8080  Frontend (NGINX, static HTML/CSS/JS)
          └──→ :8000  Backend (FastAPI, JSON only)

Backend  ──→ PostgreSQL  :5432   (User · Habit · HabitLog)
         ──→ LocalStack  :4566   (S3 — habit photos)
         ──→ Jaeger OTLP :4317   (OpenTelemetry tracing)
         ──→ /metrics    →  Prometheus :9090  →  Grafana :3000
```

- **Frontend** ve **Backend** tamamen ayrı: backend HTML üretmez, frontend NGINX'ten static serve edilir, aralarındaki iletişim CORS açık `fetch()` ile.
- **Tek `.env` dosyası** — backend, docker-compose ve k8s ConfigMap aynı kaynaktan okur.

Detaylı diyagram: [docs/architecture.png](docs/architecture.png)

---

## 🚀 Hızlı Başlangıç

```bash
cp .env.example .env
docker-compose up -d --build
```

| Servis | URL | Açıklama |
|---|---|---|
| **Frontend UI** | http://localhost:8080 | Login · Register · Dashboard |
| **Backend API** | http://localhost:8000 | REST endpoint'leri |
| **Swagger UI** | http://localhost:8000/docs | Interaktif API dokümanı |
| **ReDoc** | http://localhost:8000/redoc | Alternatif API dokümanı |
| **/health** | http://localhost:8000/health | Sağlık kontrolü (JSON) |
| **/metrics** | http://localhost:8000/metrics | Prometheus formatı |
| **Grafana** | http://localhost:3000 | admin / admin · 3 panel |
| **Prometheus** | http://localhost:9090 | Metrik sorgu UI |
| **Jaeger UI** | http://localhost:16686 | Distributed tracing (+5 bonus) |
| **LocalStack** | http://localhost:4566 | S3 emülatörü (Community Edition) |

---

## 📡 API Endpoint'leri

| # | Method | Path | Auth | Açıklama |
|---|---|---|---|---|
| 1 | POST | `/register` | – | Yeni kullanıcı |
| 2 | POST | `/login` | – | JWT token |
| 3 | POST | `/habits` | ✓ | Habit oluştur |
| 4 | GET | `/habits` | ✓ | Habit listesi |
| 5 | POST | `/habits/{id}/track` | ✓ | Bugün yap (UPSERT) |
| 6 | GET | `/habits/{id}/streak` | ✓ | Mevcut seri |
| 7 | POST | `/habits/{id}/photo` | ✓ | S3'e fotoğraf yükle |
| 8 | GET | `/habits/{id}/photos` | ✓ | S3'teki fotoğrafları listele |
| – | GET | `/health` | – | Sağlık |
| – | GET | `/metrics` | – | Prometheus |
| – | GET | `/docs` | – | Swagger UI |

---

## 🎨 Frontend UI

Dashboard'da her habit için sunulan etkileşimler:

- **"Bugün Yaptım"** — tracking ekler, streak'i günceller
- **"📸 Fotoğraf Yükle"** — file picker → `POST /habits/{id}/photo` (LocalStack S3)
- **"Fotoğrafları Listele"** — `GET /habits/{id}/photos` ile S3'teki tüm key'leri çeker

Yani LocalStack'in upload+list özellikleri direkt kullanıcı arayüzünde.

---

## ✅ Testler

### Unit + Integration (pytest, %88+ coverage)

```bash
cd backend
python -m venv .venv && .venv/Scripts/activate     # Windows
pip install -r requirements.txt
pytest tests/unit tests/integration
```

**30 test, coverage %88+**.

### Testcontainers (gerçek PostgreSQL)

```bash
pytest tests/test_testcontainers.py
```

> Windows'ta psycopg2 hostname encoding sorunu nedeniyle otomatik skip. Linux/CI'da çalışır.

### E2E (Playwright — 5 senaryo)

```bash
docker-compose up -d
pip install -r tests/e2e/requirements.txt
playwright install chromium
pytest tests/e2e/
```

### Postman/Newman (CI'da koşar)

```bash
newman run postman/collection.json --env-var base_url=http://localhost:8000
```

### Performans (k6)

```bash
k6 run -e BASE_URL=http://localhost:8000 perf/smoke-test.js
k6 run -e BASE_URL=http://localhost:8000 perf/load-test.js
```

→ p(95)=~285ms · 0% hata · detay: [perf/report.md](perf/report.md)

---

## ☸️ Kubernetes (Kind)

```bash
kind create cluster --name habit-tracker

# Build + load images
docker build -t backend:dev ./backend
docker build -t frontend:dev ./frontend
kind load docker-image backend:dev --name habit-tracker
kind load docker-image frontend:dev --name habit-tracker

# Image placeholder replace
sed -i 's|__BACKEND_IMAGE__|backend:dev|g; s|__FRONTEND_IMAGE__|frontend:dev|g' k8s/*.yaml

# Infra apply (sırayla)
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/localstack.yaml
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/prometheus.yaml
kubectl apply -f k8s/grafana.yaml
kubectl rollout status deployment/postgres --timeout=2m

# App apply
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl rollout status deployment/backend --timeout=3m

# Erişim
kubectl port-forward svc/frontend 8080:80 &
kubectl port-forward svc/backend 8000:8000 &
kubectl port-forward svc/jaeger 16686:16686 &
kubectl port-forward svc/grafana 3000:3000 &

# Temizlik
kind delete cluster --name habit-tracker
```

**K8s'de çalışan 7 servis**: postgres, backend, frontend, localstack, jaeger, prometheus, grafana.

### ArgoCD GitOps (+5 bonus)

Kurulum + sync için bkz. [k8s/argocd/README.md](k8s/argocd/README.md). Her `git push origin main` → otomatik deploy.

---

## 🔄 CI/CD Pipeline

`.github/workflows/ci.yml` — **5 job zincirli**:

```
push/PR → main
   │
   ├── lint           flake8
   ├── test           pytest + coverage 70%+ + Testcontainers
   ├── newman         live API (Postgres service) + Postman collection
   ├── build          backend + frontend → GHCR (:sha, :latest)
   └── deploy-smoke   Kind cluster + ALL infra + curl + k6 smoke
```

**`deploy-smoke` ayağa kaldırdığı servisler**: postgres, localstack, jaeger, prometheus, grafana, backend, frontend (7 servis).

---

## 📁 Proje Yapısı

```
habit-tracker-simple/
├── .env.example            # Tek kaynak config (docker-compose env_file)
├── backend/                # FastAPI REST API
│   ├── src/
│   │   ├── main.py         # 8 endpoint
│   │   ├── models.py       # User, Habit, HabitLog
│   │   ├── schemas.py      # Pydantic
│   │   ├── auth.py         # JWT + bcrypt
│   │   ├── s3_client.py    # LocalStack boto3
│   │   ├── tracing.py      # OpenTelemetry → Jaeger
│   │   ├── config.py       # pydantic-settings
│   │   └── database.py
│   ├── tests/              # 30 unit+integration + 3 testcontainers
│   ├── Dockerfile          # Multi-stage
│   └── requirements.txt
├── frontend/               # Static + NGINX
│   ├── *.html              # index, register, dashboard
│   ├── css/style.css
│   ├── js/                 # config, api, login, register, dashboard
│   ├── Dockerfile          # NGINX
│   └── nginx.conf
├── tests/e2e/              # Playwright 5 senaryo
├── k8s/                    # 7 servis manifesti
│   ├── configmap.yaml
│   ├── postgres.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   ├── localstack.yaml
│   ├── jaeger.yaml         # +5 bonus
│   ├── prometheus.yaml
│   ├── grafana.yaml
│   └── argocd/             # +5 bonus GitOps
│       ├── application.yaml
│       └── README.md
├── perf/                   # k6 smoke + load
├── postman/                # Newman collection
├── monitoring/             # docker-compose için provisioning
├── docs/                   # architecture.png + final-report.pdf
├── .github/workflows/ci.yml
├── docker-compose.yml      # 8 servis
└── LICENSE
```

---

## 📋 Şartname Karşılama

| Gereksinim | Durum | Detay |
|---|:-:|---|
| Mini Servis (4-6 endpoint) | ✅ | 6 ana + 2 S3 + 3 utility = 11 endpoint |
| Pytest unit+integration ≥%70 | ✅ | **30 test, %88 coverage** |
| Postman/Newman CI | ✅ | 7 istek + test assertions, CI'da koşar |
| Docker multi-stage | ✅ | backend (builder+runtime) + frontend (NGINX) |
| LocalStack S3 (Community Edition) | ✅ | Habit photo upload+list, UI'da görünür |
| Testcontainers ≥2 test | ✅ | 3 test (gerçek PostgreSQL 16) |
| Factory Boy + Faker | ✅ | UserFactory, HabitFactory, HabitLogFactory |
| Kubernetes (Kind) | ✅ | 7 servis manifesti |
| GitHub Actions | ✅ | lint → test → newman → build → deploy-smoke |
| Prometheus + Grafana ≥3 panel | ✅ | Request rate, error rate, p95/p99 latency |
| k6 + p95 ölçüm | ✅ | p(95)=~285ms |
| E2E 3-5 senaryo | ✅ | 5 Playwright testi |
| docs/architecture.png | ✅ | matplotlib generate |
| docs/final-report.pdf | ✅ | 5 sayfa IEEE formatı |
| **Bonus +5: OpenTelemetry** | ✅ | FastAPI+SQLAlchemy auto-instrument → Jaeger OTLP |
| **Bonus +5: ArgoCD GitOps** | ✅ | `k8s/argocd/application.yaml` — automated sync |

**Beklenen puan**: 100 + 10 bonus = **110/100**

---

## ⚙️ Konfigürasyon Mantığı

**Tek kaynak**: `.env.example` → `cp .env.example .env` → backend, docker-compose, k8s ConfigMap aynı değişkenleri kullanır.

| Değişken | Açıklama |
|---|---|
| `DATABASE_URL` | Postgres bağlantı string'i |
| `SECRET_KEY` | JWT imzalama |
| `AWS_ENDPOINT_URL` | LocalStack S3 endpoint |
| `S3_BUCKET` | Habit fotoğrafları için bucket adı |
| `ENABLE_TRACING` | `true` = Jaeger'a span gönder, `false` = kapalı |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Jaeger OTLP gRPC adresi |

---

## 📄 Lisans

MIT — bkz. [LICENSE](LICENSE)

## 🧑‍💻 Yazar

**Mert Baytaş** — Marmara Üniversitesi, Bilgisayar Mühendisliği
MTH2526-B25 — 2025-2026 Bahar
