"""docs/slides.pdf — sunum slaytları (landscape, şartname 8.3 yapısı)."""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable,
)

PAGE = landscape(A4)
os.makedirs("docs", exist_ok=True)
doc = SimpleDocTemplate("docs/slides.pdf", pagesize=PAGE,
                        leftMargin=2 * cm, rightMargin=2 * cm,
                        topMargin=1.6 * cm, bottomMargin=1.4 * cm)

styles = getSampleStyleSheet()
PRIMARY = colors.HexColor("#4f46e5")
DARK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")

slide_title = ParagraphStyle("st", parent=styles["Title"], fontSize=30,
                             textColor=PRIMARY, alignment=TA_LEFT, spaceAfter=6)
slide_sub = ParagraphStyle("ss", parent=styles["Normal"], fontSize=14,
                           textColor=MUTED, spaceAfter=16)
bullet = ParagraphStyle("b", parent=styles["Normal"], fontSize=15, leading=26,
                        textColor=DARK, leftIndent=10)
big = ParagraphStyle("bg", parent=styles["Normal"], fontSize=17, leading=30,
                     textColor=DARK)


def hr():
    return HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=14)


def B(t):
    return Paragraph(f"●&nbsp;&nbsp;{t}", bullet)


def slide(story, title, sub, body):
    story.append(Paragraph(title, slide_title))
    if sub:
        story.append(Paragraph(sub, slide_sub))
    story.append(hr())
    story += body
    story.append(PageBreak())


def tbl(data, widths, header=PRIMARY):
    t = Table(data, colWidths=[w * cm for w in widths])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f6fb")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


story = []

# ── Kapak ─────────────────────────────────────────────────────
story += [
    Spacer(1, 90),
    Paragraph("Habit Tracker", ParagraphStyle("c", parent=styles["Title"],
              fontSize=46, textColor=PRIMARY, alignment=TA_CENTER)),
    Spacer(1, 10),
    Paragraph("Basit bir uygulama · Endüstri standardı test &amp; dağıtım altyapısı",
              ParagraphStyle("c2", parent=styles["Normal"], fontSize=16,
                             textColor=MUTED, alignment=TA_CENTER)),
    Spacer(1, 40),
    Paragraph("Mert Baytaş · Marmara Üniversitesi · Bulut Mimarilerinde Test Mühendisliği",
              ParagraphStyle("c3", parent=styles["Normal"], fontSize=13,
                             textColor=DARK, alignment=TA_CENTER)),
    Paragraph("https://vivabit.digital",
              ParagraphStyle("c4", parent=styles["Normal"], fontSize=14,
                             textColor=PRIMARY, alignment=TA_CENTER)),
    PageBreak(),
]

# ── 1. Problem & Çözüm ────────────────────────────────────────
slide(story, "1 · Problem & Çözüm", "Neden test pipeline'ı?", [
    B("<b>Konu:</b> Habit Tracker API — günlük alışkanlık takibi, streak hesaplama"),
    B("<b>Amaç:</b> Karmaşık uygulama değil; basit uygulamaya <b>üretim kalitesinde test &amp; deploy altyapısı</b>"),
    B("Frontend (NGINX) + Backend (FastAPI) <b>ayrı mikroservisler</b>"),
    B("Tüm katmanlar otomatik test edilip GitOps ile canlıya çıkıyor"),
    B("<b>Canlı:</b> https://vivabit.digital — gerçek k3s cluster'da"),
])

# ── 2. Mimari ─────────────────────────────────────────────────
story.append(Paragraph("2 · Mimari Diyagram", slide_title))
story.append(hr())
if os.path.exists("docs/architecture.png"):
    story.append(Image("docs/architecture.png", width=13 * cm, height=15.5 * cm))
story.append(PageBreak())

# ── 3. Test Stratejisi ────────────────────────────────────────
slide(story, "3 · Test Stratejisi", "Test piramidi — 42+ otomatik test", [
    tbl([
        ["Katman", "Araç", "Adet"],
        ["Unit", "pytest", "8"],
        ["Integration", "pytest + TestClient", "22"],
        ["Testcontainers", "gerçek PostgreSQL 16", "6"],
        ["E2E", "Playwright", "6"],
        ["API", "Postman / Newman", "7"],
        ["Performans", "k6 (smoke + load)", "2"],
    ], [6, 9, 3]),
    Spacer(1, 14),
    B("Coverage hedefi <b>%70</b> → ulaşılan: <b>%88</b>"),
    B("Factory Boy + Faker ile izole, gerçekçi test verisi"),
])

# ── 4. CI/CD Pipeline ─────────────────────────────────────────
slide(story, "4 · CI/CD Pipeline", "GitHub Actions — 6 job, fail-fast zincir", [
    Paragraph('<font face="Courier" size="14">lint → test → newman → build → deploy-smoke → cd-bump</font>',
              big),
    Spacer(1, 14),
    B("<b>build:</b> backend + frontend imajları → GHCR (:sha, :latest)"),
    B("<b>deploy-smoke:</b> Kind cluster + Helm template + curl + k6 (kalite kapısı)"),
    B("<b>cd-bump:</b> Helm values.yaml image tag güncelle → commit"),
    B("<b>ArgoCD</b> commit'i görür → k3s cluster'a otomatik sync (GitOps)"),
])

# ── 5. Monitoring & Observability ─────────────────────────────
slide(story, "5 · Monitoring & Observability", "Prometheus + Grafana + Jaeger", [
    B("<b>Prometheus:</b> http_requests_total, request_duration histogram"),
    B("<b>Grafana:</b> 3 panel — request rate, error rate, p95/p99 latency"),
    B("<b>Jaeger (+5 bonus):</b> OpenTelemetry OTLP ile distributed tracing"),
    B("Tüm paneller BasicAuth ile korunuyor (jaeger / prometheus / api)"),
    B("grafana.vivabit.digital · jaeger.vivabit.digital · prometheus.vivabit.digital"),
])

# ── 6. Sayılar ────────────────────────────────────────────────
slide(story, "6 · Sayılar", "", [
    tbl([
        ["Ölçüt", "Değer"],
        ["Toplam test", "42+ (unit + integration + TC + E2E + Newman + k6)"],
        ["Coverage", "%88 (hedef %70)"],
        ["p95 latency (k6 load)", "~285 ms (eşik < 500 ms)"],
        ["Docker image", "Multi-stage backend + NGINX frontend"],
        ["K8s servis sayısı", "7 (postgres, backend, frontend, localstack, jaeger, prom, grafana)"],
        ["Bonus", "Helm +5 · ArgoCD +5 · OpenTelemetry +5"],
    ], [8, 16]),
])

# ── 7. Öğrendiklerim & Zorluklar ──────────────────────────────
slide(story, "7 · Öğrendiklerim & Zorluklar", "", [
    B("<b>Frontend/backend ayrımı:</b> NGINX reverse proxy ile tek domain, CORS yok"),
    B("<b>GitOps:</b> ArgoCD ile her push otomatik deploy — manuel kubectl yok"),
    B("<b>Güvenlik:</b> Traefik BasicAuth ile tracing/metrics panellerini koruma"),
    B("<b>Zorluk:</b> testcontainers v4 API değişikliği, DNS yayılması, cert-manager"),
    B("<b>İleride:</b> KEDA autoscaling, Helm chart'ı registry'ye publish"),
])

doc.build(story)
print("docs/slides.pdf written")
