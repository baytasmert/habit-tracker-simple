#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# Hetzner CX22 (Ubuntu 22.04) — k3s + cert-manager + ArgoCD kurulumu.
# Sunucuda tek seferlik çalıştırılır.
#
# Kullanım:
#   ssh root@<HETZNER-IP>
#   curl -sSL https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/scripts/setup-server.sh | bash
#
# Veya repo'yu klonladıktan sonra:
#   bash scripts/setup-server.sh
# ─────────────────────────────────────────────────────────────────
set -euo pipefail

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Habit Tracker Simple — Production Cluster Setup"
echo "════════════════════════════════════════════════════════════"
echo ""

# ── 0. Hazırlık ─────────────────────────────────────────────────
apt-get update -q
apt-get install -y -q curl git ca-certificates

# ── 1. k3s kur (Rancher Lightweight Kubernetes) ────────────────
echo "▸ k3s kuruluyor…"
curl -sfL https://get.k3s.io | sh -s - \
    --write-kubeconfig-mode 644 \
    --disable=servicelb     # Traefik kalsın, ServiceLB'yi devre dışı bırak

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
kubectl wait --for=condition=Ready node --all --timeout=120s

# kubectl tab tamamlama
echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' >> ~/.bashrc
echo 'source <(kubectl completion bash)' >> ~/.bashrc

# ── 2. cert-manager (Let's Encrypt için) ───────────────────────
echo "▸ cert-manager kuruluyor…"
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
kubectl wait --for=condition=Available deployment \
    --all -n cert-manager --timeout=180s

# ── 3. ArgoCD ──────────────────────────────────────────────────
echo "▸ ArgoCD kuruluyor…"
kubectl create namespace argocd 2>/dev/null || true
kubectl apply -n argocd \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/v2.10.5/manifests/install.yaml
kubectl wait --for=condition=Available deployment \
    --all -n argocd --timeout=300s

# ArgoCD UI ingress (Traefik üzerinden HTTPS — opsiyonel, kullanıcı sonra DNS ekler)
echo ""
echo "▸ ArgoCD admin şifresi:"
kubectl -n argocd get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" | base64 -d
echo ""

# ── 4. GHCR pull secret (private imaj çekmek için) ─────────────
echo ""
echo "▸ GHCR pull secret oluşturmak için:"
echo "   kubectl create secret docker-registry ghcr-pull \\"
echo "     --docker-server=ghcr.io \\"
echo "     --docker-username=<github-username> \\"
echo "     --docker-password=<github-PAT> \\"
echo "     --docker-email=<email>"
echo ""

# ── Bitti ──────────────────────────────────────────────────────
cat <<EOF

════════════════════════════════════════════════════════════
✅ Cluster hazır. Sıradakiler:

1. DNS A kayıtlarını sunucu IP'sine yönlendir:
   app.<domain>         A   $(curl -s ifconfig.me)
   api.<domain>         A   $(curl -s ifconfig.me)
   grafana.<domain>     A   $(curl -s ifconfig.me)
   jaeger.<domain>      A   $(curl -s ifconfig.me)
   prometheus.<domain>  A   $(curl -s ifconfig.me)
   argocd.<domain>      A   $(curl -s ifconfig.me)

   Domain yoksa nip.io kullanabilirsin:
   app.$(curl -s ifconfig.me | tr . -).nip.io

2. k8s/ingress.yaml ve k8s/cert-issuer.yaml içindeki
   example.com ve change-me@example.com yerine kendi
   domain ve email'ini yaz, commit'le ve push'la.

3. ArgoCD'ye Application kaydı:
   kubectl apply -f https://raw.githubusercontent.com/\
baytasmert/habit-tracker-simple/main/k8s/argocd/application.yaml

4. cert-manager Let's Encrypt issuer:
   kubectl apply -f https://raw.githubusercontent.com/\
baytasmert/habit-tracker-simple/main/k8s/cert-issuer.yaml

5. ArgoCD UI:
   kubectl port-forward svc/argocd-server -n argocd 8090:443
   https://localhost:8090     (admin / yukarıdaki şifre)

════════════════════════════════════════════════════════════
EOF
