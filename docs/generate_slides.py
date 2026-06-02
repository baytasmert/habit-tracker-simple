"""docs/slides.pdf — sunum slaytları (landscape, şartname 8.3 yapısı).

Tasarım: renkli başlık bantları, stat kartları, görsel pipeline akışı,
gömülü Grafana ekran görüntüsü, footer + sayfa no, demo + kapanış slaytları.
Türkçe karakterler için Windows TTF (Segoe UI / Arial) kaydedilir.
"""
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image,
)

# ── Türkçe karakter destekli font (Helvetica ş/ğ/ı basamıyor) ──────
FONT, FONT_B = "Helvetica", "Helvetica-Bold"
_fonts = r"C:\Windows\Fonts"
for reg, bold in [("segoeui.ttf", "segoeuib.ttf"), ("arial.ttf", "arialbd.ttf")]:
    rp, bp = os.path.join(_fonts, reg), os.path.join(_fonts, bold)
    if os.path.exists(rp) and os.path.exists(bp):
        pdfmetrics.registerFont(TTFont("UI", rp))
        pdfmetrics.registerFont(TTFont("UI-Bold", bp))
        registerFontFamily("UI", normal="UI", bold="UI-Bold", italic="UI", boldItalic="UI-Bold")
        FONT, FONT_B = "UI", "UI-Bold"
        break

PAGE = landscape(A4)                 # 29.7 x 21.0 cm
W, H = PAGE
CONTENT_W = 26.5                     # cm (kenar boşlukları 1.6cm)

PRIMARY = colors.HexColor("#4f46e5")
PRIMARY_D = colors.HexColor("#3730a3")
INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
LIGHT = colors.HexColor("#f3f4ff")

os.makedirs("docs", exist_ok=True)

# ── Stiller ────────────────────────────────────────────────────────
band_title = ParagraphStyle("bt", fontName=FONT, fontSize=20, textColor=colors.white, leading=22)
band_num = ParagraphStyle("bn", fontName=FONT_B, fontSize=22, textColor=colors.white, alignment=TA_CENTER)
bullet = ParagraphStyle("b", fontName=FONT, fontSize=14.5, leading=24, textColor=INK, leftIndent=6)
note = ParagraphStyle("n", fontName=FONT, fontSize=12.5, leading=20, textColor=MUTED)
card_big = ParagraphStyle("cb", fontName=FONT, fontSize=11, alignment=TA_CENTER,
                          textColor=colors.white, leading=15)
chip = ParagraphStyle("ch", fontName=FONT_B, fontSize=11.5, alignment=TA_CENTER, textColor=colors.white)
arrow = ParagraphStyle("ar", fontName=FONT_B, fontSize=15, alignment=TA_CENTER, textColor=MUTED)
cover_title = ParagraphStyle("ct", fontName=FONT_B, fontSize=52, leading=58, textColor=PRIMARY, alignment=TA_CENTER)
cover_sub = ParagraphStyle("cs", fontName=FONT, fontSize=17, textColor=INK, alignment=TA_CENTER, leading=24)
caption = ParagraphStyle("cap", fontName=FONT, fontSize=11, textColor=MUTED, alignment=TA_CENTER)
big_center = ParagraphStyle("bc", fontName=FONT_B, fontSize=42, leading=48, textColor=PRIMARY, alignment=TA_CENTER)


def band(num, title, sub=""):
    """Renkli başlık bandı: numara çipi + başlık/alt başlık."""
    nump = Paragraph(str(num), band_num)
    subhtml = f'<br/><font size="11" color="#dfe3ff">{sub}</font>' if sub else ""
    titlep = Paragraph(f'<b>{title}</b>{subhtml}', band_title)
    t = Table([[nump, titlep]], colWidths=[1.9 * cm, (CONTENT_W - 1.9) * cm], rowHeights=[1.7 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PRIMARY_D),
        ("BACKGROUND", (1, 0), (1, 0), PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (1, 0), (1, 0), 16),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 0),
    ]))
    return t


def cards(items, h=3.0):
    """Büyük sayı kartları sırası. items: (big, label, hexcolor)."""
    n = len(items)
    gap = 0.5
    cw = (CONTENT_W - gap * (n - 1)) / n
    row, widths, styles = [], [], [("VALIGN", (0, 0), (-1, -1), "MIDDLE")]
    for i, (b, label, color) in enumerate(items):
        ci = len(row)
        row.append(Paragraph(
            f'<font size="28" color="#ffffff"><b>{b}</b></font><br/><br/>'
            f'<font size="11.5" color="#ffffff">{label}</font>', card_big))
        widths.append(cw * cm)
        styles.append(("BACKGROUND", (ci, 0), (ci, 0), colors.HexColor(color)))
        if i < n - 1:
            row.append("")
            widths.append(gap * cm)
    t = Table([row], colWidths=widths, rowHeights=[h * cm])
    t.setStyle(TableStyle(styles))
    return t


def flow(steps):
    """Görsel pipeline: renkli çipler arasında oklar."""
    row, widths, styles = [], [], [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 6),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
    for i, s in enumerate(steps):
        ci = len(row)
        row.append(Paragraph(s, chip))
        widths.append(3.65 * cm)
        styles.append(("BACKGROUND", (ci, 0), (ci, 0), PRIMARY))
        if i < len(steps) - 1:
            row.append(Paragraph("&#8594;", arrow))
            widths.append(0.72 * cm)
    t = Table([row], colWidths=widths, rowHeights=[1.15 * cm])
    t.setStyle(TableStyle(styles))
    return t


def info_tbl(data, widths):
    t = Table(data, colWidths=[w * cm for w in widths])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), FONT_B),
        ("FONTNAME", (0, 1), (-1, -1), FONT),
        ("FONTSIZE", (0, 0), (-1, -1), 12.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def B(t):
    return Paragraph(f'<font color="#4f46e5"><b>•</b></font>&nbsp;&nbsp;{t}', bullet)


def slide(story, num, title, sub, body):
    story.append(band(num, title, sub))
    story.append(Spacer(1, 0.55 * cm))
    story += body
    story.append(PageBreak())


# ── Sayfa dekorasyonu (footer + üst aksan) ─────────────────────────
def deco(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, H - 0.32 * cm, W, 0.32 * cm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#e5e7eb"))
    canvas.setLineWidth(0.7)
    canvas.line(1.6 * cm, 1.02 * cm, W - 1.6 * cm, 1.02 * cm)
    canvas.setFont(FONT, 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.6 * cm, 0.62 * cm,
                      "Habit Tracker · Bulut Mimarilerinde Test Mühendisliği · Mert Baytaş")
    canvas.drawRightString(W - 1.6 * cm, 0.62 * cm, f"vivabit.digital · {doc.page}")
    canvas.restoreState()


def cover_deco(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(PRIMARY)
    canvas.rect(0, H - 3.0 * cm, W, 3.0 * cm, fill=1, stroke=0)
    canvas.setFillColor(PRIMARY_D)
    canvas.rect(0, 0, W, 1.5 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT_B, 12)
    canvas.drawString(1.8 * cm, H - 1.95 * cm,
                      "BULUT MİMARİLERİNDE TEST MÜHENDİSLİĞİ — DÖNEM PROJESİ")
    canvas.drawRightString(W - 1.8 * cm, H - 1.95 * cm, "#3 Habit Tracker API")
    canvas.setFont(FONT, 10.5)
    canvas.drawCentredString(W / 2, 0.55 * cm,
                             "Mert Baytaş · Marmara Üniversitesi · MTH2526-B25 · 2025–2026 Bahar")
    canvas.restoreState()


story = []

# ── Kapak ──────────────────────────────────────────────────────────
story += [
    Spacer(1, 5.0 * cm),
    Paragraph("Habit Tracker", cover_title),
    Spacer(1, 0.25 * cm),
    Paragraph("Basit bir uygulama · <b>üretim kalitesinde</b> test &amp; dağıtım altyapısı", cover_sub),
    Spacer(1, 1.1 * cm),
    cards([
        ("115/100", "Beklenen puan", "#10b981"),
        ("+15", "Bonus (tavan)", "#f59e0b"),
        ("7", "K8s servisi", "#3b82f6"),
        ("58", "Otomatik test", "#8b5cf6"),
    ], h=2.7),
    PageBreak(),
]

# ── 1. Problem & Çözüm ──────────────────────────────────────────────
slide(story, 1, "Problem &amp; Çözüm", "Neden bir test &amp; dağıtım pipeline'ı?", [
    B("<b>Konu:</b> Habit Tracker API — günlük alışkanlık takibi, streak ve mood"),
    B("<b>Amaç:</b> Uygulamayı değil, etrafındaki <b>üretim kalitesinde test &amp; deploy altyapısını</b> kurmak"),
    B("Frontend (NGINX) ve Backend (FastAPI) tamamen <b>ayrı mikroservisler</b>"),
    B("Her katman otomatik test edilip <b>GitOps</b> ile canlıya çıkıyor"),
    B("<b>Canlı:</b> https://vivabit.digital — gerçek bir VPS'te k3s cluster'ında"),
])

# ── 2. Mimari ───────────────────────────────────────────────────────
arch_body = []
if os.path.exists("docs/architecture.png"):
    _arch = Image("docs/architecture.png", width=11.6 * cm, height=13.8 * cm)
    _arch.hAlign = "CENTER"
    arch_body += [_arch,
                  Spacer(1, 0.15 * cm),
                  Paragraph("Browser → Traefik (HTTPS) → Frontend/Backend → Postgres · S3 · Jaeger · Prometheus · Grafana",
                            caption)]
else:
    arch_body.append(B("docs/architecture.png bulunamadı"))
story.append(band(2, "Mimari Diyagram", "Tüm bileşenler tek sayfada"))
story.append(Spacer(1, 0.3 * cm))
story += arch_body
story.append(PageBreak())

# ── 3. Test Stratejisi ──────────────────────────────────────────────
slide(story, 3, "Test Stratejisi", "Test piramidi — geniş taban, dar tepe", [
    info_tbl([
        ["Katman", "Araç", "Adet", "Kapsam"],
        ["Unit", "pytest", "8", "auth, model, Factory Boy"],
        ["Integration", "pytest + TestClient", "32", "endpoint + auth + mood + foto"],
        ["Testcontainers", "gerçek PostgreSQL 16", "3", "kalıcılık doğrulama"],
        ["E2E", "Playwright", "6", "tarayıcıda kullanıcı akışı"],
        ["API", "Postman / Newman", "7", "CI'da canlı API"],
        ["Performans", "k6 (smoke + load)", "2", "p95 latency"],
    ], [4.2, 6.5, 2.3, 8.0]),
    Spacer(1, 0.45 * cm),
    cards([
        ("%86", "coverage (hedef %70)", "#10b981"),
        ("58", "toplam otomatik test", "#4f46e5"),
        ("6", "farklı test türü", "#8b5cf6"),
    ], h=2.3),
])

# ── 4. CI/CD Pipeline ───────────────────────────────────────────────
slide(story, 4, "CI/CD Pipeline", "GitHub Actions — 6 job, fail-fast zincir", [
    flow(["lint", "test", "newman", "build", "deploy-smoke", "cd-bump"]),
    Spacer(1, 0.5 * cm),
    B("<b>test:</b> pytest + coverage (CI kapısı %70) + Testcontainers"),
    B("<b>build:</b> backend + frontend imajları → GHCR (:sha, :latest)"),
    B("<b>deploy-smoke:</b> Kind cluster + Helm + curl /health + k6 (kalite kapısı)"),
    B("<b>cd-bump:</b> Helm values.yaml image tag güncelle → commit"),
    B("<b>ArgoCD</b> commit'i görür → k3s cluster'a otomatik sync — manuel kubectl yok"),
])

# ── 5. Monitoring & Observability ───────────────────────────────────
mon_body = []
if os.path.exists("docs/grafana-dashboard.png"):
    _graf = Image("docs/grafana-dashboard.png", width=20 * cm, height=9.46 * cm)
    _graf.hAlign = "CENTER"
    mon_body += [_graf,
                 Spacer(1, 0.12 * cm),
                 Paragraph("Grafana — request rate · error rate · p95/p99 latency (canlı: grafana.vivabit.digital)",
                           caption)]
else:
    mon_body += [B("<b>Grafana:</b> request rate · error rate · p95/p99 latency"),
                 B("<b>Prometheus:</b> http_requests_total, request_duration histogram")]
story.append(band(5, "Monitoring &amp; Observability", "Prometheus + Grafana + Jaeger (OpenTelemetry)"))
story.append(Spacer(1, 0.3 * cm))
story += mon_body
story.append(PageBreak())

# ── 6. Sayılar ──────────────────────────────────────────────────────
story.append(band(6, "Sayılar", "Projeyi tek bakışta özetleyen metrikler"))
story.append(Spacer(1, 0.7 * cm))
story.append(cards([
    ("58", "otomatik test", "#4f46e5"),
    ("%86", "coverage", "#10b981"),
    ("~285ms", "p95 (yük testi)", "#f59e0b"),
], h=3.3))
story.append(Spacer(1, 0.6 * cm))
story.append(cards([
    ("7", "K8s servisi", "#3b82f6"),
    ("6", "CI job", "#8b5cf6"),
    ("+15", "bonus (Helm·OTel·ArgoCD)", "#ef4444"),
], h=3.3))
story.append(PageBreak())

# ── 7. Öğrendiklerim & Zorluklar ────────────────────────────────────
slide(story, 7, "Öğrendiklerim &amp; Zorluklar", "En akılda kalanlar", [
    B("<b>Servis ayrımı:</b> NGINX reverse proxy ile tek origin — CORS derdi yok"),
    B("<b>GitOps:</b> ArgoCD ile her push otomatik deploy; selfHeal manuel değişikliği geri alır"),
    B("<b>Gözlemlenebilirlik tuzağı:</b> Service'i scrape etmek 2 replikanın sayaçlarını "
      "karıştırıp sahte spike üretti → pod bazlı scrape ile çözüldü"),
    B("<b>Kalıcılık:</b> Postgres'e PVC eklenince restart'ta veri korunuyor"),
    B("<b>İleride:</b> KEDA ile event-driven autoscaling, Helm chart'ı registry'ye publish"),
])

# ── 8. Canlı Demo Akışı ─────────────────────────────────────────────
slide(story, 8, "Canlı Demo Akışı", "~7 dakika", [
    B("<b>1.</b> PR aç → GitHub Actions yeşil olmaya başlar"),
    B("<b>2.</b> PR merge → image build + push (GHCR)"),
    B("<b>3.</b> ArgoCD yeni versiyonu k3s'e otomatik sync eder"),
    B("<b>4.</b> Grafana'da deploy sonrası latency / error rate panelleri"),
    B("<b>5.</b> k6 ile kısa load testi → p95 latency"),
    B("<b>6.</b> Playwright ile 1–2 E2E senaryosu canlı koşar"),
    B("<b>Yedek:</b> canlı çökerse demo videosu"),
])

# ── 9. Kapanış ──────────────────────────────────────────────────────
story += [
    Spacer(1, 3.4 * cm),
    Paragraph("Teşekkürler", big_center),
    Spacer(1, 0.4 * cm),
    Paragraph("Sorular &amp; canlı demo", cover_sub),
    Spacer(1, 1.0 * cm),
    cards([
        ("Uygulama", "vivabit.digital", "#4f46e5"),
        ("API Docs", "api.vivabit.digital/docs", "#3b82f6"),
        ("Grafana", "grafana.vivabit.digital", "#10b981"),
        ("Tracing", "jaeger.vivabit.digital", "#f59e0b"),
    ], h=3.0),
]

doc = SimpleDocTemplate("docs/slides.pdf", pagesize=PAGE,
                        leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                        topMargin=1.5 * cm, bottomMargin=1.5 * cm)
doc.build(story, onFirstPage=cover_deco, onLaterPages=deco)
print("docs/slides.pdf written")
