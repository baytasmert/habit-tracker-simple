# ArgoCD GitOps Setup

`k8s/argocd/application.yaml` — bu repo'nun `k8s/` klasörünü cluster'a sync eden ArgoCD `Application` manifesti.

## Tek seferlik kurulum

```bash
# 1) ArgoCD'yi cluster'a kur
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl wait --for=condition=available --timeout=300s \
  deployment/argocd-server -n argocd

# 2) UI'a eriş
kubectl port-forward svc/argocd-server -n argocd 8090:443
# → https://localhost:8090
# User: admin
# Password:
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# 3) Application'ı oluştur
kubectl apply -f k8s/argocd/application.yaml
```

## Sonuç

- ArgoCD repo'yu watch eder.
- Her `git push origin main` → otomatik sync, drift varsa düzeltir.
- UI'da Sync status, health, son commit görünür.

## Sunum için

Sunum öncesi `kubectl apply -f k8s/argocd/application.yaml` çalıştırılır, sonra UI gösterilir:

```
https://localhost:8090/applications/habit-tracker-simple
```

Burada her commit'in otomatik deploy edildiği canlı olarak görülür.

## Neden ayrı klasör?

`application.yaml` ArgoCD namespace'inde `Application` kaynağıdır — ana uygulamanın k8s manifestleri ile (Deployment/Service/ConfigMap) karışmaması için `k8s/argocd/` altında. ArgoCD bu klasörü `exclude` patern'iyle kendi sync'inden hariç tutar (sonsuz döngü olmasın).
