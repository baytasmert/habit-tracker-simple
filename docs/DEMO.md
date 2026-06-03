# 🎬 Canlı Demo Cheat Sheet (VPS)

Sunum demosu **VPS'ten** gösterilir. Komutlar kopyala-yapıştır hazır.

---

## A. Tek seferlik kurulum (VPS'te bir kez)
```bash
cd ~ && git clone https://github.com/baytasmert/habit-tracker-simple.git
cd habit-tracker-simple
bash scripts/setup-demo.sh  # k6 + gh + python venv + playwright (önkoşullar dahil)
gh auth login               # GitHub girişi (push/PR için — interaktif, bir kez)
```
> `scripts/setup-demo.sh` = demo araçları (idempotent). Cluster kurulumu ayrı: `scripts/setup-server.sh` (k3s/Helm/ArgoCD — tek seferlik, zaten kurulu).

---

## B. GitOps demo — yeni sürüm canlıya (hocanın istediği akış)
**Hoca:** "PR aç → CI tetikle (yeşil)" + "PR merge → CD tetikle, image build + push"

```bash
cd ~/habit-tracker-simple && git checkout main && git pull --no-rebase

# 1) Branch + görünür değişiklik (footer sürüm rozetini artır)
git checkout -b demo/canli
sed -i 's/Sürüm v1.0/Sürüm v1.1/' frontend/index.html

# 2) Commit + push + PR  →  CI burada tetiklenir (Adım 1: "PR aç → CI")
git add frontend/index.html
git commit -m "demo: sürüm v1.1"
git push -u origin demo/canli
gh pr create --fill --base main
gh pr checks --watch              # CI yeşil olmaya başlar (lint→test→build→smoke)

# 3) Merge  →  CD tetiklenir: build image push + cd-bump (Adım 2: "merge → CD")
gh pr merge --merge --delete-branch

# 4) ArgoCD deploy'u izle, sonra vivabit.digital'i yenile → "Sürüm v1.1" canlı
kubectl -n argocd annotate application habit-tracker-simple argocd.argoproj.io/refresh=hard --overwrite
kubectl get application habit-tracker-simple -n argocd -w
```
⏱️ Tam tur ~6 dk CI + ~1-3 dk ArgoCD → **slot başında başlat**, demoda sonucu göster.

---

## C. k6 yük testi — **1 dk'lık QUICK mod** (p95)
```bash
cd ~/habit-tracker-simple
k6 run -e QUICK=1 -e BASE_URL=https://vivabit.digital/api perf/load-test.js
```
- `QUICK=1` → 10 VU, 30 sn sabit yük (~1 dk'da biter). Süre/VU: `-e DURATION=20s -e VUS=15`.
- Tam test (rapor metodu, ~60s+): `QUICK` olmadan çalıştır.
- Çıktıda: `http_req_duration ... p(95)=...` + `http_req_failed`.
> ⚠️ VPS'te koşunca k6 host CPU'sunu kullanır → Grafana "Host CPU" panelinde k6 yükü de görünür (normal).

---

## D. K8s / ArgoCD komutları (deploy göster + sorun ayıkla)
```bash
kubectl get application habit-tracker-simple -n argocd   # Synced? Healthy?
kubectl get pods                                          # hepsi Running mi
kubectl get pvc                                           # postgres-data / prometheus-data Bound mu

kubectl get pods -w                          # rolling update CANLI (eski→yeni pod)
kubectl rollout status deployment/backend
kubectl describe deployment backend | grep -i image       # çalışan :sha

kubectl logs deploy/backend --tail=50
kubectl describe pod <pod-adı>               # Pending/CrashLoop sebebi
```

---

## E. Manuel E2E (1 senaryo, canlıya karşı)
```bash
cd ~/habit-tracker-simple && . .venv-e2e/bin/activate
FRONTEND_URL=https://vivabit.digital \
  pytest tests/e2e/test_user_flow.py -k "register_login or track" -v
deactivate
```
> VPS başsız (headless) → tarayıcı görünmez, **PASS/FAIL çıktısı** gösterilir. Tarayıcıyı canlı izletmek istersen laptop'tan `--headed` ile koş.

---

## 🎯 Önerilen demo sırası (≤7 dk)
1. **Slot başında:** B'deki PR'ı aç + merge et (CI + ArgoCD arka planda çalışsın).
2. Slaytlar (~8 dk).
3. Demo: **CI yeşil** (gh / Actions) → **ArgoCD Synced** (D) → `vivabit.digital` "v1.1" **canlı** → **Grafana** panelleri → **k6 QUICK** (C) → **1 E2E** (E).

## 📌 GitOps best-practice (savunma notu)
Hocanın "PR→CI, merge→CD" akışı = endüstri standardı **deployment gate**:
- **PR aç → CI** = quality gate (lint/test/coverage/smoke). Bozuk kod merge edilse de **prod'a gidemez**.
- **PR merge → CD** = `build` imajı GHCR'a push'lar + `cd-bump` values.yaml tag'ini bump'lar → **ArgoCD** otomatik sync.
- **CI kırmızıysa `cd-bump` çalışmaz** → prod eski/sağlam sürümde kalır (fail-fast + deployment gate).
- Daha sıkı: branch protection "require status checks" ile kırmızı PR merge bile edilemez (ekip ortamı için).

## ❓ SSS — Hocanın beklediği sorular (hazır cevaplar)

### "Deploy stratejisi ne?"
**GitOps + deployment gate.** Tek doğruluk kaynağı **Git**:
`push → CI (lint→test→newman→build→deploy-smoke) → cd-bump values.yaml'a yeni :sha yazar → ArgoCD git'i görüp k3s'e otomatik sync (rolling update)`.
- Backend/frontend her merge'de yeni `:sha` ile güncellenir; üçüncü-parti imajlar (Jaeger/Postgres...) **pinned** (sabit sürüm, sürpriz yok).
- CI kırmızıysa `cd-bump` çalışmaz → **bozuk kod prod'a gidemez.**
- Postgres `Recreate` + PVC; diğerleri rolling update. Manuel `kubectl` yok.

### "Deploy çökerse rollback nasıl yapılır?"
Dört yol (en hızlısı üstte):
```bash
# 1) ArgoCD — önceki sağlıklı revizyona dön (UI: History & Rollback, veya CLI)
argocd app rollback habit-tracker-simple

# 2) Git revert — bozuk commit'i geri al, ArgoCD eski hali uygular
git revert <bozuk-commit> && git push        # GitOps: Git neyse cluster o

# 3) İmaj geri al — values.yaml'daki tag'i önceki :sha'ya çevir → push
#    (GHCR'de her commit'in imajı :sha ile duruyor)

# 4) Kubernetes native (acil)
kubectl rollout undo deployment/backend
```
> selfHeal açık → elle yapılan sapmayı ArgoCD zaten Git'e göre geri alır. `:sha` etiketi sayesinde "hangi sürüme döneceğim" hep belli.

### "Coverage neden buradan düşük?"
**%87 toplam** (CI gate %70). Düşük yerler **bilinçli**:
- `s3_client.py` (~%30), `tracing.py` (~%22) → bunlar **entegrasyon kodu** (LocalStack/Jaeger). Unit test yerine **gerçek servisle** doğrulanır: Testcontainers (gerçek Postgres) + E2E (gerçek tarayıcı).
- Saf iş mantığı (`auth`, `models`, `schemas`, `main`) → **%95+**.
- Yani %100 hedef değil; **anlamlı kapsama** hedef. Entegrasyon kodu kendi katmanında (E2E/Testcontainers) test edilir.

### "Bu kod satırı ne yapıyor?" (rastgele dosya)
Önce **katmanı** söyle: `templates/*.yaml`→Helm/K8s, `src/auth.py`→JWT, `conftest.py`→test fixture, `tracing.py`→OpenTelemetry. Sonra satırı açıkla.

### "Multi-stage Dockerfile neden?"
Builder katmanı bağımlılıkları derler; runtime katmanı sadece sonucu taşır → küçük + güvenli imaj (derleyici prod imajında yok).

---

## ⚠️ Hatırlatmalar
- `gh auth login` **bu gece dene** (demoda sürpriz olmasın).
- k6 + E2E canlıya **gerçek test verisi** yazar (sorun değil, demo sonrası kalır).
- **Rapor/slayt** VPS'te değil; teslim GitHub'dan/lokalden.
- Postgres/Prometheus PVC ilk geçişte veriyi **bir kez** sıfırlamış olabilir (sonrası kalıcı).
