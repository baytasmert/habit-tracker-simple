"""docs/architecture.png üretir — güncel mimari (Helm + ArgoCD + VPS)."""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


def box(ax, x, y, w, h, label, sub='', color='#3498DB'):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.08",
                          facecolor=color, edgecolor='white',
                          linewidth=1.5, alpha=0.93, zorder=3)
    ax.add_patch(rect)
    cx, cy = x + w / 2, y + h / 2
    if sub:
        ax.text(cx, cy + 0.10, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=4)
        ax.text(cx, cy - 0.20, sub, ha='center', va='center',
                fontsize=7, color='white', alpha=0.9, zorder=4)
    else:
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=4)


def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.2),
                zorder=5)
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.09, label,
                ha='center', va='bottom', fontsize=6.5, color='#444', zorder=6)


def section(ax, x, y, w, h, label, color='#ECF0F1'):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='#BDC3C7',
                          linewidth=1, alpha=0.3, zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.15, y + h - 0.15, label, ha='left', va='top',
            fontsize=7, color='#555', style='italic', zorder=2)


fig, ax = plt.subplots(figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

# Title
ax.text(8, 9.65, 'Habit Tracker — Mimari Diyagram',
        ha='center', fontsize=14, fontweight='bold', color='#2C3E50')
ax.text(8, 9.3, 'FastAPI · PostgreSQL · LocalStack · Prometheus · Grafana · Jaeger · k3s · Helm · ArgoCD · vivabit.digital',
        ha='center', fontsize=7.5, color='#7F8C8D')

# ── Sections ──────────────────────────────────────────────────────
section(ax, 0.2, 6.0, 15.6, 3.0, 'Internet / Client')
section(ax, 0.2, 2.0, 15.6, 3.7, 'VPS: k3s Kubernetes — app.vivabit.digital vb.')
section(ax, 0.2, 0.2, 7.5, 1.6, 'CI/CD — GitHub Actions')
section(ax, 8.0, 0.2, 7.8, 1.6, 'GitOps — ArgoCD')

# ── Internet layer ────────────────────────────────────────────────
box(ax, 0.5, 6.8, 2.0, 1.0, 'Browser', 'User / Playwright E2E', '#4A90D9')
box(ax, 3.2, 6.8, 2.5, 1.0, 'Traefik', 'Ingress + Let\'s Encrypt\nHTTPS terminasyon', '#E67E22')

# ── K8s layer ─────────────────────────────────────────────────────
box(ax, 0.5, 3.8, 2.0, 1.2, 'Frontend', 'NGINX :80\nstatic HTML/JS/CSS', '#E67E22')
box(ax, 3.2, 3.8, 2.2, 1.2, 'Backend', 'FastAPI :8000\nREST API (JSON)', '#27AE60')
box(ax, 6.2, 3.8, 2.0, 1.2, 'PostgreSQL', ':5432\nUser/Habit/Log', '#8E44AD')
box(ax, 9.0, 3.8, 2.0, 1.2, 'LocalStack', 'S3 :4566\nHabit photos', '#E74C3C')
box(ax, 11.2, 3.8, 2.0, 1.2, 'Prometheus', ':9090\n/metrics scrape', '#D35400')
box(ax, 13.4, 3.8, 2.0, 1.2, 'Grafana', ':3000\n3 panel dashboard', '#2980B9')
box(ax, 6.2, 2.2, 2.0, 1.2, 'Jaeger', ':16686 UI\nOTLP :4317', '#16A085')

# Helm chart label
ax.text(7.5, 5.3, '⎈  helm/habit-tracker (Helm Chart — +5 bonus)',
        ha='center', fontsize=8, color='#2C3E50',
        bbox=dict(boxstyle='round,pad=0.3', facecolor='#FEF9E7', edgecolor='#F0C040'))

# ── CI/CD ─────────────────────────────────────────────────────────
box(ax, 0.4, 0.4, 3.2, 1.2, 'GitHub Actions', 'lint→test→newman\nbuild→smoke', '#7F8C8D')
box(ax, 3.9, 0.4, 3.5, 1.2, 'GHCR Registry', 'backend:sha\nfrontend:sha', '#2C3E50')

# ── ArgoCD ───────────────────────────────────────────────────────
box(ax, 8.2, 0.4, 3.0, 1.2, 'ArgoCD', 'GitOps +5 bonus\nrepo watch → sync', '#E91E63')
box(ax, 11.5, 0.4, 3.8, 1.2, 'GitHub Repo', 'helm/values.yaml\nimage tag bump', '#24292E')

# ── Arrows ────────────────────────────────────────────────────────
# Browser → Traefik
arrow(ax, 2.5, 7.3, 3.2, 7.3, 'HTTPS')
# Traefik → Frontend
arrow(ax, 4.5, 6.8, 1.5, 5.0, 'app.')
# Traefik → Backend
arrow(ax, 5.0, 6.8, 4.3, 5.0, 'api.')
# Traefik → Grafana
arrow(ax, 5.7, 7.0, 14.4, 5.0, 'grafana.')
# Frontend → Backend
arrow(ax, 3.2, 4.4, 2.5, 4.4, 'fetch /api')
# Backend → Postgres
arrow(ax, 5.4, 4.4, 6.2, 4.4, 'SQLAlchemy')
# Backend → LocalStack
arrow(ax, 5.4, 4.0, 9.0, 4.0, 'boto3 S3')
# Backend → Prometheus
arrow(ax, 5.4, 4.8, 11.2, 4.8, '/metrics')
# Backend → Jaeger
arrow(ax, 4.3, 3.8, 6.9, 3.4, 'OTLP gRPC')
# Prometheus → Grafana
arrow(ax, 13.2, 4.4, 13.4, 4.4, 'scrape')
# CI → GHCR
arrow(ax, 3.6, 1.0, 3.9, 1.0, 'push :sha')
# GHCR → ArgoCD (tag bump)
arrow(ax, 7.4, 1.0, 8.2, 1.0, 'cd-bump')
# ArgoCD → GitHub Repo
arrow(ax, 11.2, 1.0, 11.5, 1.0, 'watch')
# ArgoCD → K8s
arrow(ax, 9.7, 1.6, 5.0, 3.8, 'helm upgrade')

os.makedirs('docs', exist_ok=True)
plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa')
print('docs/architecture.png written')
