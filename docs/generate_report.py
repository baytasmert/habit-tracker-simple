"""docs/final-report.pdf üretir — 5 sayfa, ders şartname formatı."""
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
h1 = ParagraphStyle('h1', parent=styles['Heading1'], fontSize=13, spaceBefore=10,
                   spaceAfter=6, textColor=colors.HexColor('#27AE60'))
h2 = ParagraphStyle('h2', parent=styles['Heading2'], fontSize=11, spaceBefore=8,
                   spaceAfter=4, textColor=colors.HexColor('#2980B9'))
body = ParagraphStyle('b', parent=styles['Normal'], fontSize=10, leading=14,
                     alignment=TA_JUSTIFY, spaceAfter=6)
bullet = ParagraphStyle('bl', parent=styles['Normal'], fontSize=10, leading=13,
                       leftIndent=14, spaceAfter=3)


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
    'dagiitiim altyapisini</b> kurmaktir. Bu yuzden uygulama 6 endpoint ile '
    'sinirli; mimari ise tum sartname katmanlarini (Docker, K8s, CI/CD, '
    'monitoring, perf, E2E) icerir.'
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
        story.append(Image('docs/architecture.png', width=15 * cm, height=9 * cm))
    except Exception:
        story.append(P('[Mimari diyagram: docs/architecture.png]'))
story.append(Spacer(1, 4))
story.append(tbl([
    ['Bilesen', 'Teknoloji', 'Port', 'Rol'],
    ['Frontend', 'NGINX 1.25 + Vanilla JS', '80', 'Static HTML/CSS/JS serve'],
    ['Backend', 'FastAPI 0.110 + Python 3.11', '8000', 'REST API (JSON)'],
    ['DB', 'PostgreSQL 16', '5432', 'User, Habit, HabitLog'],
    ['S3 (LocalStack)', 'LocalStack 3', '4566', 'Habit progress photo'],
    ['Metrics', 'Prometheus 2.51', '9090', 'API metrik scrape'],
    ['Dashboard', 'Grafana 10.4', '3000', '3 panel (rate, error, latency)'],
], [3.5, 4.5, 2, 6], '#27AE60'))
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
    ['Integration', 'pytest + TestClient', '18', 'Endpoint + auth flow'],
    ['Testcontainers', 'testcontainers-python', '3', 'Gercek PostgreSQL container'],
    ['E2E', 'Playwright', '5', 'Tarayicida register/login/track/logout'],
    ['API', 'Postman/Newman', '7', 'CI da koşar'],
    ['Perf', 'k6', '2', 'Smoke (3VU/15s) + Load (20VU/60s)'],
], [3, 4, 1.5, 7.5], '#2980B9'))
story.append(H2('3.1 Coverage Hedefi'))
story.append(P(
    'Hedef >= %70. Olcum: <b>%94</b> (src/auth, models, schemas, main coverage). '
    'pyproject.toml icinde --cov-fail-under=70 ile CI da zorunlu kilindi.'
))
story.append(H2('3.2 Factory Boy + Faker'))
story.append(P(
    'tests/factories.py icinde UserFactory, HabitFactory, HabitLogFactory '
    'tanimlanmistir. Her test izole, gercekci ama unique veri kullanir.'
))

# ── 4. CI/CD ─────────────────────────────────────────────
story.append(H1('4. CI/CD Pipeline'))
story.append(P(
    '.github/workflows/ci.yml — tek workflow, 4 job:'
))
story.append(tbl([
    ['Job', 'Amac', 'Onkos'],
    ['lint', 'flake8 kod stili kontrolu', '-'],
    ['test', 'pytest + coverage 70+%', 'lint'],
    ['build', 'Docker (backend+frontend) -> GHCR (:sha)', 'test'],
    ['deploy-smoke', 'Kind cluster apply + curl /health', 'build'],
], [3, 7, 4], '#16A085'))
story.append(P(
    'Build job iki Docker imaj uretir (backend + frontend), her ikisi de '
    'GitHub Container Registry e :sha + :latest etiketleriyle pushlanir. '
    'Deploy job ayni imajlari Kind cluster a yukler, k8s/*.yaml manifestlerini '
    'sed ile render edip apply eder.'
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
    ['Toplam Test', '34 (8 unit + 18 integration + 3 TC + 5 E2E)'],
    ['Test Coverage', '%94'],
    ['p(95) Latency', '~285 ms (k6 load)'],
    ['Docker Image', 'Multi-stage backend + NGINX alpine frontend'],
    ['K8s Manifest', 'ConfigMap + Postgres + Backend + Frontend (4 dosya)'],
    ['Grafana Panel', '3 panel (rate, errors, latency)'],
    ['CI Job', '4 (lint, test, build, deploy-smoke)'],
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
story.append(H2('6.2 Ileride'))
story += [
    B('Helm chart paketleme (bonus +5)'),
    B('OpenTelemetry tracing (bonus +5)'),
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
