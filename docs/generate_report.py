"""docs/final-report.pdf üretir — 6 sayfa, 11pt / 1.15, ders şartname formatı."""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image,
)

os.makedirs('docs', exist_ok=True)
doc = SimpleDocTemplate(
    'docs/final-report.pdf', pagesize=A4,
    rightMargin=2.4 * cm, leftMargin=2.4 * cm,
    topMargin=2.2 * cm, bottomMargin=2.2 * cm,
)
styles = getSampleStyleSheet()

title = ParagraphStyle('t', parent=styles['Title'], fontSize=18, alignment=TA_CENTER,
                      textColor=colors.HexColor('#2C3E50'))
sub = ParagraphStyle('s', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER,
                    textColor=colors.HexColor('#7F8C8D'))
h1 = ParagraphStyle('h1', parent=styles['Heading1'], fontSize=13, spaceBefore=7,
                   spaceAfter=4, textColor=colors.HexColor('#27AE60'))
h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=11, spaceBefore=6,
                   spaceAfter=3, textColor=colors.HexColor('#2980B9'))
# Sartname format: 11pt yazi, 1.15 satir araligi (11 * 1.15 ~= 12.65 leading)
body = ParagraphStyle('b', parent=styles['Normal'], fontSize=11, leading=12.65,
                     alignment=TA_JUSTIFY, spaceAfter=4)
bullet = ParagraphStyle('bl', parent=styles['Normal'], fontSize=11, leading=12.65,
                       leftIndent=14, spaceAfter=2)


def H1(t): return Paragraph(t, h1)
def H2(t): return Paragraph(t, h2)
def P(t): return Paragraph(t, body)
def B(t): return Paragraph(f'• {t}', bullet)
def hr():
    return HRFlowable(width='100%', thickness=0.5,
                      color=colors.HexColor('#BDC3C7'), spaceAfter=8)


def tbl(data, widths, header='#27AE60'):
    t = Table(data, colWidths=[w * cm for w in widths])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1),
         [colors.white, colors.HexColor('#F4F6F7')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#BDC3C7')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


story = []

# ── Cover ─────────────────────────────────────────────────
story += [
    Spacer(1, 30),
    Paragraph('Habit Tracker (Simple)', title),
    Paragraph('Bulut Mimarilerinde Test Muhendisligi — Final Rapor', sub),
    Spacer(1, 8),
    hr(),
]
meta = [
    ['Ogrenci', 'Mert Baytas'],
    ['Ders', 'MTH2526-B25 — Bulut Mimarilerinde Test Muhendisligi'],
    ['Egitmen', 'Busra Ayaksiz'],
    ['Konu', '#3 Habit Tracker API'],
    ['Teslim', '4 Haziran 2026'],
    ['Repo', 'github.com/baytasmert/habit-tracker-simple'],
]
story.append(tbl(meta, [4, 12], '#2C3E50'))
story += [Spacer(1, 20), hr(), PageBreak()]

# ── 1. Giris ─────────────────────────────────────────────
story.append(H1('1. Giris'))
story.append(P(
    'Bu proje, Marmara Universitesi Bilgisayar Muhendisligi bolumunun "Bulut '
    'Mimarilerinde Test Muhendisligi" dersi kapsaminda gelistirilmis bireysel '
    'donem projesidir. Konu olarak #3 <b>Habit Tracker API</b> secilmistir: '
    'gunluk aliskanlik takibi, streak hesaplama ve REST API. '
    'Bu, ayni hesabin "habit-tracker-api" reposunun lightweight versiyonudur — '
    'sartnamenin minimum gereksinimlerini karsilayan, savunulmasi kolay basit '
    'bir mimari kurulmustur.'
))
story.append(P(
    'Amac uygulamayi karmasiklastirmak degil, endustri standardinda <b>test ve '
    'dagiitiim altyapisini</b> kurmaktir. Uygulama 14 endpoint (auth, habit CRUD, '
    'gunluk track + mood, S3 foto) ile sade tutuldu; mimari ise tum sartname '
    'katmanlarini (Docker, K8s/Helm, CI/CD, monitoring, perf, E2E) icerir.'
))

# ── 2. Mimari ────────────────────────────────────────────
story.append(H1('2. Mimari'))
story.append(P(
    'Sistem iki bagimsiz servis olarak tasarlanmistir: <b>frontend</b> '
    '(NGINX, sadece static dosya) ve <b>backend</b> (FastAPI, sadece JSON '
    'REST). Bu ayrim, gercek uretim mimarilerinin ana ozelligidir; ayrica '
    'her bir servisin bagimsiz olcekleneblmesini saglar.'
))
if os.path.exists('docs/architecture.png'):
    try:
        story.append(Image('docs/architecture.png', width=9.2 * cm, height=10.95 * cm))
    except Exception:
        story.append(P('[Mimari diyagram: docs/architecture.png]'))
story.append(Spacer(1, 4))
story.append(tbl([
    ['Bilesen', 'Teknoloji', 'Port', 'Rol'],
    ['Frontend', 'NGINX 1.25 + Vanilla JS', '80', 'Static HTML/CSS/JS serve'],
    ['Backend', 'FastAPI 0.110 + Python 3.11', '8000', 'REST API (JSON)'],
    ['DB', 'PostgreSQL 16', '5432', 'User, Habit, HabitLog'],
    ['S3 (LocalStack)', 'LocalStack 3', '4566', 'Habit progress photo'],
    ['Tracing', 'Jaeger 1.55', '16686', 'OTLP span (bonus +5)'],
    ['Metrics', 'Prometheus 2.51', '9090', 'API metrik scrape'],
    ['Dashboard', 'Grafana 10.4', '3000', '3 panel (rate, error, latency)'],
], [3.5, 4.5, 2, 6], '#27AE60'))
story.append(P(
    'Uretim ortami: tek VPS uzerinde <b>k3s</b> cluster, <b>Helm</b> chart ile '
    'deploy, <b>Traefik</b> ingress (HTTPS / Let\'s Encrypt) ve <b>ArgoCD</b> ile '
    'GitOps otomatik senkronizasyon. Tum servisler vivabit.digital alt alanlari '
    'uzerinden yayinlanir.'
))
story.append(PageBreak())

# ── 3. Test Stratejisi ───────────────────────────────────
story.append(H1('3. Test Stratejisi'))
story.append(P(
    'Test piramidi yaklasimi: cok sayida birim test, orta sayida entegrasyon, '
    'az sayida E2E. Toplam testler ve hedef coverage:'
))
story.append(tbl([
    ['Katman', 'Arac', 'Adet', 'Aciklama'],
    ['Unit', 'pytest', '8', 'auth + model + Factory Boy'],
    ['Integration', 'pytest + TestClient', '32', 'Endpoint + auth + log/mood + photo'],
    ['Testcontainers', 'testcontainers-python', '3', 'Gercek PostgreSQL container'],
    ['E2E', 'Playwright', '6', 'Tarayicida register/login/track/logout'],
    ['API', 'Postman/Newman', '7', 'CI da koşar'],
    ['Perf', 'k6', '2', 'Smoke (3VU/15s) + Load (20VU/60s)'],
], [3, 4, 1.5, 7.5], '#2980B9'))
story.append(H2('3.1 Coverage Hedefi'))
story.append(P(
    'Hedef >= %70. Olcum: <b>%86</b> (src/auth, models, schemas, main coverage). '
    'pyproject.toml icinde --cov-fail-under=70 ile CI da zorunlu kilindi. '
    'Toplam birim+entegrasyon test sayisi: <b>40</b>.'
))
story.append(H2('3.2 Factory Boy + Faker'))
story.append(P(
    'tests/factories.py icinde UserFactory, HabitFactory, HabitLogFactory '
    'tanimlanmistir. Her test izole, gercekci ama unique veri kullanir.'
))

# ── 4. Pipeline & Deploy ─────────────────────────────────
story.append(H1('4. Pipeline & Deploy'))
story.append(H2('4.1 GitHub Actions'))
story.append(P(
    '.github/workflows/ci.yml — tek workflow, 6 job zincirli:'
))
story.append(tbl([
    ['Job', 'Amac', 'Onkos'],
    ['lint', 'flake8 kod stili kontrolu', '-'],
    ['test', 'pytest + coverage 70+%', 'lint'],
    ['newman', 'Postman koleksiyonu canli API ye (Postgres service)', 'lint'],
    ['build', 'Docker (backend+frontend) -> GHCR (:sha, :latest)', 'test, newman'],
    ['deploy-smoke', 'Kind cluster + helm template apply + curl + k6', 'build'],
    ['cd-bump', 'values.yaml imaj tag bump -> commit (ArgoCD tetikler)', 'deploy-smoke'],
], [2.5, 9.5, 4], '#16A085'))
story.append(P(
    'Build job iki Docker imaj uretir (backend + frontend), her ikisi de '
    'GitHub Container Registry e :sha + :latest etiketleriyle pushlanir. '
    'Deploy job ayni imajlari Kind cluster a yukler ve Helm chart i '
    '<i>helm template ... | kubectl apply -f -</i> ile render edip uygular; '
    'ardindan /health + /metrics curl ve k6 smoke ile dogrular. Son olarak '
    'cd-bump job u Helm values.yaml deki imaj tag ini yeni SHA ya gunceller; '
    'uretimdeki ArgoCD bu commit i gorup cluster i otomatik senkronize eder.'
))
story.append(H2('4.2 Kubernetes Manifestleri & Deploy Stratejisi'))
story.append(P(
    '7 servisin tum K8s kaynaklari (Deployment + Service + ConfigMap + Ingress) '
    'tek bir <b>Helm chart</b> (helm/habit-tracker) icinde template lenmistir; '
    'imaj tag, domain, replica ve kaynak limitleri values.yaml dan yonetilir. '
    'Ayni chart hem CI deki Kind cluster da (ingress kapali, port-forward) hem de '
    'uretimdeki k3s cluster da (ingress acik, Traefik + Let\'s Encrypt) calisir. '
    'Deploy stratejisi <b>GitOps</b> tir: git push -> CI imaj build + values tag '
    'bump -> ArgoCD farki algilayip otomatik sync eder. Rollback, ArgoCD de '
    'onceki saglikli revizyona donmek veya GHCR deki :sha etiketli onceki imaja '
    'gecmek kadar basittir.'
))
story.append(PageBreak())

# ── 5. Monitoring & Perf ─────────────────────────────────
story.append(H1('5. Monitoring ve Performans'))
story.append(H2('5.1 Prometheus Metrikleri'))
story.append(tbl([
    ['Metrik', 'Tur', 'Aciklama'],
    ['http_requests_total', 'Counter', 'Endpoint/method/status bazli sayim'],
    ['http_request_duration_seconds', 'Histogram', 'p50/p95/p99 latency'],
], [5.5, 2.5, 8], '#D35400'))
story.append(H2('5.2 Grafana Dashboard (3 panel)'))
story.append(B('Request Rate: <code>rate(http_requests_total[1m])</code> by endpoint'))
story.append(B('Error Rate: 4xx/5xx oranlari, status koduna gore'))
story.append(B('Latency p95/p99: <code>histogram_quantile</code> ile hesaplanir'))
# Grafana ekran goruntusu (docs/grafana-dashboard.png varsa otomatik eklenir)
if os.path.exists('docs/grafana-dashboard.png'):
    try:
        story.append(Spacer(1, 4))
        story.append(Image('docs/grafana-dashboard.png', width=15 * cm, height=7.5 * cm))
    except Exception:
        story.append(P('[Grafana dashboard: grafana.vivabit.digital]'))
else:
    story.append(P(
        '<i>Canli dashboard: grafana.vivabit.digital (ekran goruntusu icin '
        'docs/grafana-dashboard.png eklenebilir).</i>'
    ))
story.append(H2('5.3 k6 Sonuclari'))
story.append(tbl([
    ['Test', 'VU', 'Sure', 'p(95)', 'Hata', 'Sonuc'],
    ['Smoke', '3', '15s', '~5 ms', '0%', 'PASS'],
    ['Load', '10->20', '60s', '~285 ms', '0%', 'PASS'],
], [2, 2, 2, 2.5, 2, 2], '#E74C3C'))
story.append(Spacer(1, 4))
story.append(P(
    '<b>Yorum:</b> p(95)=285 ms hedef olan 500 ms in cok altinda. '
    'En yavas endpoint ler /register ve /login — bcrypt password hashing '
    'guvenlik gereksinimi, optimize edilmez. Detayli rapor: '
    '<code>perf/report.md</code>.'
))

# ── 6. Sonuc ─────────────────────────────────────────────
story.append(H1('6. Sonuc ve Ogrendiklerim'))
story.append(tbl([
    ['Olcut', 'Deger'],
    ['Toplam Test', '40 birim+entegrasyon + 3 TC + 6 E2E + 7 Newman'],
    ['Test Coverage', '%86 (CI gate: --cov-fail-under=70)'],
    ['p(95) Latency', '~285 ms (k6 load)'],
    ['Docker Image', 'Multi-stage backend + NGINX alpine frontend'],
    ['K8s Deploy', 'Helm chart -> 7 servis (k3s prod + Kind CI)'],
    ['Grafana Panel', '3 panel (rate, errors, latency)'],
    ['CI Job', '6 (lint, test, newman, build, deploy-smoke, cd-bump)'],
    ['Bonus', 'Helm +5, OpenTelemetry +5, ArgoCD +5 (tavan +15)'],
], [6, 10], '#2C3E50'))
story.append(H2('6.1 Zorluklar'))
story += [
    B('<b>Frontend ayrimi:</b> Ilk versiyonda Jinja2 ile FastAPI icine '
      'gomuluydu — bu projede NGINX uzerinden static serve edilen tamamen '
      'ayri bir servis olarak yeniden tasarlandi. Bu, mikroservis '
      'mimarilerinin temel ayrimini ogretti.'),
    B('<b>Testcontainers Windows encoding:</b> psycopg2, Windows Turkce '
      'locale ile uyumlu calismadi. Cozum: pytestmark ile platforma ozel '
      'skip, Linux/CI da otomatik calisir.'),
    B('<b>K8s image render:</b> Manifestlerde imaj etiketi GitHub SHA degisken — '
      'sed ile placeholder degistirme calisti.'),
]
story.append(H2('6.2 Tamamlanan Bonuslar'))
story += [
    B('<b>Helm chart (+5):</b> 7 servisin tum K8s kaynaklari tek chart ta '
      'paketlendi; imaj tag/domain/replica values.yaml dan yonetilir.'),
    B('<b>OpenTelemetry tracing (+5):</b> FastAPI + SQLAlchemy auto-instrument, '
      'OTLP ile Jaeger e span gonderilir.'),
    B('<b>ArgoCD GitOps (+5):</b> git push -> CI tag bump -> ArgoCD otomatik sync. '
      'Toplam bonus +15 (tavan).'),
]
story.append(H2('6.3 Ileride'))
story += [
    B('KEDA ile event-driven autoscaling (kalan tek bonus konu)'),
    B('Connection pooling (PgBouncer) — yuksek yukte daha az overhead'),
]

# ── 7. Kaynaklar ─────────────────────────────────────────
story.append(H1('7. Kaynaklar'))
sources = [
    ('FastAPI', 'fastapi.tiangolo.com'),
    ('Testcontainers Python', 'testcontainers-python.readthedocs.io'),
    ('k6', 'k6.io/docs'),
    ('Playwright Python', 'playwright.dev/python'),
    ('Kubernetes', 'kubernetes.io/docs'),
    ('Prometheus Python Client', 'github.com/prometheus/client_python'),
]
story.append(tbl([['Kaynak', 'URL']] + sources, [5, 11], '#16A085'))

story += [Spacer(1, 12), hr(), Paragraph(
    'Mert Baytas — Marmara Universitesi, Bilgisayar Muhendisligi, 2026',
    ParagraphStyle('f', parent=styles['Normal'], fontSize=8,
                   textColor=colors.gray, alignment=TA_CENTER)
)]

doc.build(story)
print('docs/final-report.pdf written')
