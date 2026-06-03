#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────
# DEMO ARAÇLARI kurulumu (k6 + gh + Playwright E2E).
# Cluster kurulumundan AYRIDIR (o: scripts/setup-server.sh — k3s/Helm/ArgoCD).
#
# Kullanım — repo klonlandıktan sonra repo kökünde:
#   cd ~/habit-tracker-simple && bash scripts/setup-demo.sh
#
# Idempotent: tekrar çalıştırmak güvenli (kurulu olanı atlar).
# ─────────────────────────────────────────────────────────────────
set -e

echo "==> 1) Önkoşullar (python venv/pip, gnupg, curl, wget)"
sudo apt-get update -y
sudo apt-get install -y python3-venv python3-pip gnupg curl wget ca-certificates

echo "==> 2) k6 (yük testi)"
if ! command -v k6 >/dev/null 2>&1; then
  sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
  echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" \
    | sudo tee /etc/apt/sources.list.d/k6.list
  sudo apt-get update -y && sudo apt-get install -y k6
else
  echo "    k6 zaten kurulu: $(k6 version | head -1)"
fi

echo "==> 3) gh (GitHub CLI) — PR/push için"
if ! command -v gh >/dev/null 2>&1; then
  sudo snap install gh || sudo apt-get install -y gh   # snap güncel sürüm; olmazsa apt
else
  echo "    gh zaten kurulu: $(gh --version | head -1)"
fi

echo "==> 4) E2E ortamı (Python venv + Playwright chromium)"
if [ -f tests/e2e/requirements.txt ]; then
  python3 -m venv .venv-e2e
  . .venv-e2e/bin/activate
  pip install --upgrade pip -q
  pip install -r tests/e2e/requirements.txt -q
  playwright install --with-deps chromium
  deactivate
  echo "    E2E ortamı hazır ✓"
else
  echo "    UYARI: tests/e2e/requirements.txt yok — repo kökünden çalıştır."
fi

echo ""
echo "==> DEMO ARAÇLARI HAZIR."
echo "    Son adım (elle, interaktif):  gh auth login"
echo "    (push/PR için GitHub girişi şart — bir kez yap.)"
