"""docs/final-report.pdf üretir — 7 sayfa, 11pt / 1.15, ders şartname formatı."""
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
        story.append(Image('docs/architecture.png', width=9.0 * cm, height=10.71 * cm))
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
    ['Dashboard', 'Grafana 10.4', '3000', '12 panel (API + host + kapasite)'],
], [3.5, 4.5, 2, 6], '#27AE60'))
story.append(P(
    'Uretim ortami: tek VPS uzerinde <b>k3s</b> cluster, <b>Helm</b> chart ile '
    'deploy, <b>Traefik</b> ingress (HTTPS / Let\'s Encrypt) ve <b>ArgoCD</b> ile '
    'GitOps otomatik senkronizasyon. Tum servisler vivabit.digital alt alanlari '
    'uzerinden yayinlanir.'
))
story.append(H2('2.1 Frontend ve Backend'))
story.append(P(
    '<b>Frontend</b> (NGINX + vanilla JS): landing, login, register ve dashboard '
    'sayfalari. Dashboard ozet kartlari (toplam / bugun tamamlanan / en uzun seri), '
    'kategori renkli habit kartlari, haftalik ilerleme cubugu, 5 emoji mood secici '
    've fotograf yukleme sunar. Backend HTML uretmez; iletisim NGINX <i>/api</i> '
    'reverse proxy uzerinden (tek origin, CORS yok).'
))
story.append(P(
    '<b>Backend</b> (FastAPI): yalniz JSON REST, 14 endpoint, JWT + bcrypt auth. '
    'Ana endpoint ler:'
))
story.append(tbl([
    ['Method', 'Path', 'Aciklama'],
    ['POST', '/register · /login', 'Kayit + JWT token'],
    ['GET / POST', '/habits', 'Habit listele / olustur'],
    ['POST', '/habits/{id}/track', 'Gunu isaretle (UPSERT + mood)'],
    ['GET', '/habits/{id}/streak · /logs', 'Seri + toplam, gunluk gecmis'],
    ['POST / GET', '/habits/{id}/photo(s)', 'S3 foto yukle / listele / goruntule'],
    ['GET', '/health · /metrics · /docs', 'Saglik, Prometheus, Swagger'],
], [2.6, 6.2, 7.2], '#8E44AD'))
if os.path.exists('docs/website.png'):
    try:
        _web = Image('docs/website.png', width=8.5 * cm, height=7.85 * cm)
        _web.hAlign = 'CENTER'
        story.append(Spacer(1, 4))
        story.append(_web)
        story.append(Paragraph('Uygulama arayuzu — dashboard (vivabit.digital)', sub))
    except Exception:
        pass
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
    '<b>Fail-fast zincir:</b> bir job kirilirsa sonrakiler calismaz — bozuk kod '
    'build/deploy edilmez. build imajlari GHCR a (:sha) pushlar; deploy-smoke '
    'gercek bir Kind cluster da deploy edip dogrular (kalite kapisi).'
))
story.append(H2('4.2 Deploy Stratejisi (GitOps)'))
story.append(P(
    '7 servisin tum K8s kaynaklari tek bir <b>Helm chart</b> ta toplandi; '
    'values.yaml sayesinde ayni chart lokal / CI / prod ta calisir (imaj tag, '
    'domain, replica oradan). Deploy <b>GitOps</b> tir: <b>ArgoCD</b> git i '
    'surekli izler, fark olunca cluster i otomatik sync eder. Rollback = onceki '
    'Git revizyonu veya :sha etiketli onceki imaj.'
))
story.append(B(
    '<b>Yeni guncelleme akisi:</b> kod degisikligi &#8594; PR (CI tum testleri '
    'kosar, prod a dokunulmaz) &#8594; merge &#8594; imaj GHCR a push + cd-bump '
    'values.yaml a yeni :sha yazar &#8594; ArgoCD git i gorup k3s e rolling '
    'update ile uygular. Manuel kubectl yok; tek dogruluk kaynagi Git.'
))
story.append(PageBreak())

# ── 5. Monitoring & Perf ─────────────────────────────────
story.append(H1('5. Monitoring ve Performans'))
story.append(H2('5.1 Grafana Dashboard (12 panel)'))
story.append(tbl([
    ['Panel', 'Ne gosterir (kisaca)'],
    ['Ozet kartlari', 'Erisilebilirlik %, aktif kullanici (5dk), saglikli pod'],
    ['Kapasite', 'Aktif kullanici vs host CPU/RAM (zaman bazli korelasyon)'],
    ['Host CPU/RAM/Disk + Uptime', 'VM kaynak kullanimi + backend ayakta suresi'],
    ['Istek / Hata / Gecikme', 'Endpoint req/s, 4xx-5xx orani, p95/p99 latency'],
    ['Gercek API Yuku', 'Endpoint bazli yuk dagilimi (probe/scrape haric)'],
], [5, 11], '#2980B9'))
# Grafana ekran goruntusu: guncel grafana.png varsa onu, yoksa eskisini
_graf = 'docs/grafana.png' if os.path.exists('docs/grafana.png') else 'docs/grafana-dashboard.png'
if os.path.exists(_graf):
    try:
        story.append(Spacer(1, 4))
        _gh = 8.04 if _graf.endswith('grafana.png') else 7.56
        _gi = Image(_graf, width=16 * cm, height=_gh * cm)
        _gi.hAlign = 'CENTER'
        story.append(_gi)
        story.append(Paragraph('Grafana — API & servis metrikleri (grafana.vivabit.digital)', sub))
    except Exception:
        story.append(P('[Grafana dashboard: grafana.vivabit.digital]'))
story.append(H2('5.2 k6 Sonuclari'))
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
    ['Build Suresi', '~1 dk (backend + frontend imaj -> GHCR)'],
    ['CI Pipeline', '~5-6 dk (6 job: lint -> cd-bump)'],
    ['Prod Deploy', 'ArgoCD otomatik sync ~1-3 dk (cd-bump sonrasi)'],
    ['Docker Image', 'Multi-stage backend + NGINX alpine frontend'],
    ['K8s Deploy', 'Helm chart -> 7 servis (k3s prod + Kind CI)'],
    ['Grafana Panel', '12 panel (API + host + kapasite)'],
    ['Bonus', 'Helm +5, OpenTelemetry +5, ArgoCD +5 (tavan +15)'],
], [6, 10], '#2C3E50'))
story.append(H2('6.1 Ogrendiklerim ve Zorluklar'))
story += [
    B('<b>Gozlemlenebilirlik tuzagi:</b> Grafana /health i 1-2K istek/s '
      'gosteriyordu, ama gercek hiz ~0.2/s idi. Sebep: Prometheus Service i '
      'scrape edince 2 replikanin sayaclari tek seriye karisip rate() sahte '
      'spike uretiyordu. Her pod u ayri scrape (kubernetes_sd + RBAC) ile '
      'cozuldu. Metrige korkmadan once dogrulamak gerektigini ogrendim.'),
    B('<b>Kapasite / CPU throttling:</b> k6 yukunde p95 13 s e firladi ama host '
      'CPU sadece %37 idi -> darbogaz makine degil, pod un 0.5 CPU limiti '
      '(Kubernetes throttling) + her iterasyonda bcrypt. CPU limitini artirip '
      'yuk testini gercekci yaparak (VU basina tek login) cozdum.'),
    B('<b>Metrik kardinalitesi:</b> Etikette ham URL (/habits/1/track) her id yi '
      'ayri seri yapip kardinaliteyi patlatiyordu. Route sablonu '
      '(/habits/{habit_id}/track) ile tek seride topladim.'),
    B('<b>Kalicilik:</b> Postgres ve Prometheus baslangicta volume suz idi -> '
      'restart ta veri/metrik gidiyordu. PVC ekleyerek kalici kildim (stateless '
      'pod ile kalici state ayrimini ogrendim).'),
    B('<b>Konfigurasyon yonetimi:</b> Servis URL leri, DB ve S3 ayarlarini kod '
      'icinde yonetmek (lokal vs CI vs prod) cok zordu. Tek kaynaktan okumaya '
      'gectim: pydantic-settings + .env / Helm values -> ayni kod her ortamda, '
      'sadece deger degisir.'),
    B('<b>Lint dengesi:</b> Basit stil kurallari (E203/E302/F401...) CI yi '
      'surekli takiyordu. <code>backend/.flake8</code> ile pragmatik bir ignore '
      'listesi hazirladim — kodu kiran hatalar yakalanir, stil takintilari gecilir.'),
]

story += [Spacer(1, 12), hr(), Paragraph(
    'Mert Baytas — Marmara Universitesi, Bilgisayar Muhendisligi, 2026',
    ParagraphStyle('f', parent=styles['Normal'], fontSize=8,
                   textColor=colors.gray, alignment=TA_CENTER)
)]

doc.build(story)
print('docs/final-report.pdf written')
