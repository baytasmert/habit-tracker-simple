"""docs/architecture.png üretir — sade mimari diyagramı."""
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
                fontsize=10, fontweight='bold', color='white', zorder=4)
        ax.text(cx, cy - 0.20, sub, ha='center', va='center',
                fontsize=7.5, color='white', alpha=0.9, zorder=4)
    else:
        ax.text(cx, cy, label, ha='center', va='center',
                fontsize=10, fontweight='bold', color='white', zorder=4)


def arrow(ax, x1, y1, x2, y2, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#7F8C8D', lw=1.4),
                zorder=5)
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.10, label,
                ha='center', va='bottom', fontsize=7, color='#444', zorder=6)


fig, ax = plt.subplots(figsize=(14, 9))
ax.set_xlim(0, 14)
ax.set_ylim(0, 9)
ax.axis('off')
ax.set_facecolor('#f8f9fa')
fig.patch.set_facecolor('#f8f9fa')

ax.text(7, 8.6, 'Habit Tracker (Simple) — Mimari',
        ha='center', fontsize=14, fontweight='bold', color='#2C3E50')
ax.text(7, 8.2, 'FastAPI · PostgreSQL · LocalStack · NGINX · Prometheus · Grafana · Kubernetes',
        ha='center', fontsize=8, color='#7F8C8D')

# Browser
box(ax, 0.5, 6.5, 2.0, 1.0, 'Browser', 'User / Playwright', '#4A90D9')

# Frontend (NGINX)
box(ax, 3.5, 6.5, 2.2, 1.0, 'Frontend', 'NGINX :80\n(static HTML/JS/CSS)', '#E67E22')

# Backend (FastAPI)
box(ax, 6.5, 6.5, 2.2, 1.0, 'Backend', 'FastAPI :8000\n(REST API only)', '#27AE60')

# Postgres
box(ax, 6.5, 4.0, 2.2, 1.2, 'PostgreSQL', ':5432\nUser/Habit/Log', '#8E44AD')

# LocalStack
box(ax, 9.5, 4.0, 2.2, 1.2, 'LocalStack', ':4566\nS3 (photos)', '#E74C3C')

# Prometheus
box(ax, 9.5, 6.5, 2.2, 1.0, 'Prometheus', ':9090', '#D35400')

# Grafana
box(ax, 12.0, 6.5, 1.5, 1.0, 'Grafana', ':3000', '#2980B9')

# Jaeger
box(ax, 9.5, 2.5, 2.2, 1.0, 'Jaeger', ':16686 / OTLP :4317', '#16A085')

# K8s box
box(ax, 0.5, 1.5, 8.5, 1.8, 'Kubernetes (Kind)', '', '#2C3E50')
ax.text(4.7, 2.7, 'Deployment + Service + ConfigMap',
        ha='center', fontsize=9, color='white')
ax.text(4.7, 2.3, '(postgres · backend ×2 · frontend ×2)',
        ha='center', fontsize=8, color='white', alpha=0.85)

# CI/CD
box(ax, 10.0, 1.5, 3.5, 1.8, 'GitHub Actions CI', '', '#7F8C8D')
ax.text(11.75, 2.7, 'lint → test → build → deploy → smoke',
        ha='center', fontsize=8.5, color='white')
ax.text(11.75, 2.3, 'GHCR images (:sha)', ha='center', fontsize=8, color='white', alpha=0.85)

# Arrows
arrow(ax, 2.5, 7.0, 3.5, 7.0, 'HTTP :80')
arrow(ax, 2.5, 6.7, 6.5, 6.7, 'fetch() → API :8000')
arrow(ax, 7.6, 6.5, 7.6, 5.2, 'SQLAlchemy')
arrow(ax, 8.7, 6.7, 9.5, 5.0, 'boto3')
arrow(ax, 8.7, 7.2, 9.5, 7.2, '/metrics')
arrow(ax, 11.7, 7.0, 12.0, 7.0, 'query')
arrow(ax, 8.7, 6.5, 9.5, 3.5, 'OTLP traces')

# CI → K8s
arrow(ax, 10.0, 2.4, 9.0, 2.4, 'kubectl apply')

os.makedirs('docs', exist_ok=True)
plt.tight_layout()
plt.savefig('docs/architecture.png', dpi=150, bbox_inches='tight',
            facecolor='#f8f9fa')
print('docs/architecture.png written')
