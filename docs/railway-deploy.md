# 🚂 Railway'e Kalıcı Deploy

Railway, GitHub'a `push` attığın anda otomatik build + deploy yapan bir PaaS. Bu rehber, projeyi 5-10 dakikada kalıcı olarak ayağa kaldırır.

## Mimari

Railway'de **3 servis** oluşturacağız:

```
[Internet] → frontend.up.railway.app (NGINX :80)
                  │
                  ├── /          → static HTML/CSS/JS
                  └── /api/*     → reverse proxy →  backend.railway.internal:8000
                                                          │
                                                          └──→ Postgres (Railway managed)
```

> LocalStack, Jaeger, Prometheus, Grafana **Railway'e gitmiyor** — bunlar lokal demo/şartname için. Production'da S3 = gerçek AWS, tracing = Honeycomb/Datadog kullanılır.

---

## Adım Adım Kurulum

### 1. Hesap aç

1. https://railway.app → "Login with GitHub"
2. GitHub yetkilendir → kendi hesabını seç
3. İlk girişte $5 deneme kredisi gelir (~2 ay yeter)

### 2. Yeni proje

1. **New Project** → **Deploy from GitHub repo**
2. Repo seç: `baytasmert/habit-tracker-simple`
3. Railway "Detected Dockerfile" diyecek — şimdilik **Skip** veya "Just deploy" — ileride yapılandıracağız

### 3. Postgres servisini ekle

1. Project ekranında **+ New** → **Database** → **Add PostgreSQL**
2. Otomatik provision olur, birkaç saniye sürer
3. Bu servisin adı `Postgres` olur — `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT` env'leri Railway tarafından otomatik üretilir

### 4. Backend servisini yapılandır

1. Project'te **+ New** → **GitHub Repo** → `habit-tracker-simple` seç
2. Settings sekmesinde:
   - **Service Name**: `Backend`
   - **Root Directory**: `backend`
   - **Watch Paths**: `backend/**` (sadece backend değişince deploy)
3. **Variables** sekmesinde şu env'leri ekle:

```
DATABASE_URL=${{Postgres.DATABASE_URL}}
SECRET_KEY=<rastgele uzun bir string üret>
ACCESS_TOKEN_EXPIRE_MINUTES=60
ENABLE_TRACING=false
S3_BUCKET=habit-photos
AWS_ENDPOINT_URL=
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
```

> `${{Postgres.DATABASE_URL}}` Railway'in cross-service reference syntax'ı — Postgres servisinin URL'sini otomatik bağlar.

4. **Networking** sekmesi:
   - **Public domain** → şimdilik **aç** (test için, sonra kapatacağız)
   - Railway sana `backend-production-XXXX.up.railway.app` verir
5. **Deploy** tıkla, ~2 dk bekle

### 5. Backend'i test et

```bash
curl https://backend-production-XXXX.up.railway.app/health
# {"status":"ok"}
```

`/docs` URL'ini de aç → Swagger UI görünmeli.

### 6. Backend'i internal yap

1. Backend → **Networking** → **Public domain** → **Remove**
2. Backend artık sadece Railway internal network'ünde — `backend.railway.internal:8000`

### 7. Frontend servisini yapılandır

1. **+ New** → **GitHub Repo** → aynı repo
2. Settings:
   - **Service Name**: `Frontend`
   - **Root Directory**: `frontend`
   - **Watch Paths**: `frontend/**`
3. Variables:

```
PORT=8080
BACKEND_URL=http://${{Backend.RAILWAY_PRIVATE_DOMAIN}}:8000
```

> `${{Backend.RAILWAY_PRIVATE_DOMAIN}}` Railway cross-reference — Backend servisinin internal hostname'ini verir.

4. **Networking** → **Generate Domain**
   - Railway sana `frontend-production-YYYY.up.railway.app` verir
   - Bu senin **kalıcı public URL'in**

### 8. Bitti

`https://frontend-production-YYYY.up.railway.app` aç → welcome sayfası gelir, kayıt ol → dashboard.

---

## Otomatik Deploy

`main` branch'ine her `git push` Railway tarafından algılanır, ilgili servis otomatik rebuild edilir. **CI/CD pipeline'ı**: artık GitHub Actions + Railway birlikte çalışır:

- GitHub Actions: lint + test + Newman + k6 (kalite kapısı)
- Railway: imaj build + canlı deploy

---

## Maliyet Yönetimi

- İlk $5 kredisi 2-3 ay yeter
- Dashboard'da **Usage** sekmesinden takip et
- Demo bitince servisleri **Pause** et → ücretlenme durur
- Tekrar sunum öncesi **Resume** → 30 saniyede ayağa kalkar

---

## Sunumda Nasıl Gösterirsin?

1. Slayt'ta canlı URL: `https://frontend-production-YYYY.up.railway.app`
2. Hocayı oraya yönlendir → kayıt olabilir, habit ekleyebilir
3. "Şu anda gördüğünüz uygulama Railway'de Kubernetes'e benzer bir container platformunda çalışıyor"
4. Q&A: "Production'da AWS EKS veya GKE'ye taşımak için k8s manifestleri hazır, sadece kubeconfig değişiyor" — `k8s/` klasörünü göster

---

## Sorun Giderme

| Hata | Çözüm |
|---|---|
| Backend 500 | Variables'tan `DATABASE_URL` doğru bağlanmış mı? Logs sekmesini aç |
| Frontend 502 Bad Gateway | `BACKEND_URL` env'i Backend internal domain'ini gösteriyor mu? |
| Build fail | Logs → genelde requirements.txt veya port çakışması |
| Postgres tablolar yok | Backend ilk açıldığında `Base.metadata.create_all` otomatik çalıştırır — restart et |
| Photo upload 500 | LocalStack Railway'de yok — bu beklenen, sadece lokal'de çalışır |

---

## Alternatif: Railway CLI ile

```bash
npm i -g @railway/cli
railway login
railway link              # repo'yu projeye bağla
railway up                # tüm servisleri deploy et
railway logs --service Backend
```
