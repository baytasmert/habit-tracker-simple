# Cloud Deploy — k3s + ArgoCD + Traefik on VPS

## Mimari

```
VPS (Ubuntu 22.04)
└── k3s (Kubernetes)
    ├── Traefik     ← ingress + otomatik HTTPS (Let's Encrypt)
    ├── cert-manager
    ├── ArgoCD      ← GitOps: repo → cluster
    └── default ns:
        ├── postgres, localstack, jaeger
        ├── prometheus, grafana
        ├── backend, frontend
        └── ingress (5 alt domain)

GitHub push → CI (lint/test/build/smoke) → cd-bump (kustomization.yaml günceller)
   → ArgoCD sync → kubectl rollout (3 dakika içinde canlı)
```

## 1. Sunucu Kurulumu

SSH bağlan:
```bash
ssh root@<VPS-IP>
```

Tek komutla kur:
```bash
curl -sSL https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/scripts/setup-server.sh | bash
```

Bu komut şunları yapar (~15 dk):
- k3s (Kubernetes) kur
- cert-manager kur (Let's Encrypt)
- ArgoCD kur
- ArgoCD admin şifresini ekrana yaz

## 2. Domain / DNS

**Domain varsa** (örn. Namecheap'ten aldıysan):
DNS panelinde 6 A kaydı ekle, hepsi → VPS IP:
```
app          A   <VPS-IP>
api          A   <VPS-IP>
grafana      A   <VPS-IP>
jaeger       A   <VPS-IP>
prometheus   A   <VPS-IP>
argocd       A   <VPS-IP>
```

**Domain yoksa** `nip.io` kullan (bedava, DNS gerektirmez):
IP: `104.249.8.24` → host: `104-249-8-24.nip.io`
```
app.104-249-8-24.nip.io
api.104-249-8-24.nip.io
grafana.104-249-8-24.nip.io
jaeger.104-249-8-24.nip.io
prometheus.104-249-8-24.nip.io
```

## 3. Repo'da Domain Güncelle

`k8s/ingress.yaml` ve `k8s/cert-issuer.yaml` içindeki `example.com` → kendi domain.

```bash
# Lokal bilgisayarda:
sed -i 's/example.com/104-249-8-24.nip.io/g' k8s/ingress.yaml
sed -i 's/change-me@example.com/senin@email.com/g' k8s/cert-issuer.yaml
git add k8s/ingress.yaml k8s/cert-issuer.yaml
git commit -m "chore: set production domain"
git push
```

## 4. GHCR Pull Secret

Sunucuda (imajları çekmek için):
```bash
kubectl create secret docker-registry ghcr-pull \
  --docker-server=ghcr.io \
  --docker-username=baytasmert \
  --docker-password=<GITHUB_PAT> \
  --docker-email=mertbaytas@gmail.com \
  -n default
```

GitHub PAT oluştur: GitHub → Settings → Developer settings → Personal access tokens → New token → `read:packages` scope yeterli.

## 5. cert-manager Issuer + ArgoCD App

```bash
# cert-manager issuer'ı apply et
kubectl apply -f https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/k8s/cert-issuer.yaml

# ArgoCD Application kaydı — bundan sonra her şey otomatik
kubectl apply -f https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/k8s/argocd/application.yaml
```

ArgoCD repo'yu ~3 dakikada sync eder, tüm deployment'lar başlar.

## 6. ArgoCD UI

```bash
kubectl port-forward svc/argocd-server -n argocd 8090:443
```
Tarayıcı: `https://localhost:8090`
- User: `admin`
- Password: kurulum sırasında ekrana basıldı, tekrar almak için:
  ```bash
  kubectl -n argocd get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d
  ```

## 7. Deployment'ları İzle

```bash
# Tüm pod'lar
kubectl get pods -w

# Backend log
kubectl logs -f deployment/backend

# ArgoCD sync durumu
kubectl -n argocd get app habit-tracker-simple
```

## 8. GitOps Akışı (Deploy)

Bundan sonra her deploy şöyle çalışır:

```
1. Kod değişikliği yap (backend/frontend/k8s)
2. git push origin main
3. GitHub Actions:
   ├── lint → test → Newman → build → Kind smoke (CI gate ~8 dk)
   └── cd-bump: kustomization.yaml'a yeni :sha tag yaz, commit'le
4. ArgoCD (VPS'de) commit'i görür (~3 dk polling)
5. kustomize build → kubectl apply → rollout
6. https://app.<domain> güncel versiyon
```

## Canlı URL'ler

| Servis | URL |
|--------|-----|
| Frontend | https://app.104-249-8-24.nip.io |
| Backend API | https://api.104-249-8-24.nip.io/docs |
| Grafana | https://grafana.104-249-8-24.nip.io |
| Jaeger | https://jaeger.104-249-8-24.nip.io |
| Prometheus | https://prometheus.104-249-8-24.nip.io |
