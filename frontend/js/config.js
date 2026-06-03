// ─────────────────────────────────────────────────────────────
// TEK KAYNAK — ortam (lokal vs prod) URL yönetimi.
// Build adımı yok: tarayıcı hostname'ine bakıp otomatik seçer.
// Yeni bir ortam URL'i lazımsa SADECE buraya ekle.
// ─────────────────────────────────────────────────────────────
const LOCAL = ["localhost", "127.0.0.1"].includes(location.hostname);

// API hep relative — NGINX /api'yi backend'e proxy'liyor (her iki ortamda çalışır)
window.API_URL = "/api";
window.TOKEN_KEY = "habit_tracker_token";

// Ortama göre değişen dış linkler
window.DOCS_URL = LOCAL
  ? "http://localhost:8000/docs"
  : "https://api.vivabit.digital/docs";

// data-docs taşıyan tüm linklere doğru href'i ata (lokal/prod otomatik)
document.querySelectorAll("a[data-docs]").forEach((a) => { a.href = window.DOCS_URL; });
