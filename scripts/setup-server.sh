#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# VPS (Ubuntu 22.04) — k3s + Helm + cert-manager + ArgoCD kurulumu
# Tek seferlik çalıştırılır.
#
# Kullanım (sunucuda):
#   curl -sSL https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/scripts/setup-server.sh | bash
# ─────────────────────────────────────────────────────────────────
set -euo pipefail

echo "════════════════════════════════════════════════════════════"
echo "  Habit Tracker — Production Cluster Setup"
echo "════════════════════════════════════════════════════════════"

# ── 0. Hazırlık ─────────────────────────────────────────────────
apt-get update -q
apt-get install -y -q curl git ca-certificates

# ── 1. k3s ──────────────────────────────────────────────────────
echo ""
echo "▸ [1/4] k3s kuruluyor…"
curl -sfL https://get.k3s.io | sh -s - --write-kubeconfig-mode 644

export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
echo 'export KUBECONFIG=/etc/rancher/k3s/k3s.yaml' >> ~/.bashrc

kubectl wait --for=condition=Ready node --all --timeout=120s
echo "  k3s hazır ✓"

# ── 2. Helm ─────────────────────────────────────────────────────
echo ""
echo "▸ [2/4] Helm kuruluyor…"
curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
echo "  Helm hazır ✓"

# ── 3. cert-manager (Helm ile) ──────────────────────────────────
echo ""
echo "▸ [3/4] cert-manager kuruluyor…"
helm repo add jetstack https://charts.jetstack.io --force-update
helm repo update

helm upgrade --install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --version v1.14.5 \
  --set installCRDs=true \
  --wait

echo "  cert-manager hazır ✓"

# ── 4. ArgoCD (Helm ile) ────────────────────────────────────────
echo ""
echo "▸ [4/4] ArgoCD kuruluyor…"
helm repo add argo https://argoproj.github.io/argo-helm --force-update
helm repo update

# server.insecure: ingress (Traefik) TLS'i sonlandırıp HTTP forward ettiği
# için ArgoCD plain HTTP serve etmeli — yoksa redirect loop olur.
# Doğru helm path: configs.params."server.insecure"
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --set 'configs.params.server\.insecure=true' \
  --wait --timeout 5m

echo "  ArgoCD hazır ✓"

# ── Bilgiler ────────────────────────────────────────────────────
ARGOCD_PASS=$(kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d)

SERVER_IP=$(curl -s ifconfig.me)

cat <<EOF

════════════════════════════════════════════════════════════
✅ Kurulum tamamlandı!

ArgoCD Bilgileri:
  kubectl port-forward svc/argocd-server -n argocd 8090:80
  URL:      http://localhost:8090
  Kullanıcı: admin
  Şifre:    ${ARGOCD_PASS}

Sunucu IP: ${SERVER_IP}
nip.io domain prefix: $(echo $SERVER_IP | tr . -)

Sıradaki adımlar:
  1. GHCR pull secret oluştur:
     kubectl create secret docker-registry ghcr-pull \\
       --docker-server=ghcr.io \\
       --docker-username=baytasmert \\
       --docker-password=<GITHUB_PAT> \\
       --docker-email=mertbaytas@gmail.com

  2. cert-manager issuer kur:
     kubectl apply -f https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/k8s/cert-issuer.yaml

  3. ArgoCD Application kur:
     kubectl apply -f https://raw.githubusercontent.com/baytasmert/habit-tracker-simple/main/k8s/argocd/application.yaml

  4. Deploy izle:
     kubectl get pods -w
════════════════════════════════════════════════════════════
EOF
