if (!window.auth.requireAuth()) {
  throw new Error("Redirecting to login");
}

const listEl = document.getElementById("habits-list");
const form = document.getElementById("new-habit-form");
const newError = document.getElementById("new-habit-error");
const createBtn = document.getElementById("create-habit-btn");
const logoutBtn = document.getElementById("logout-btn");
const toggleAdd = document.getElementById("toggle-add");

const CATEGORY_EMOJI = { health: "🏥", fitness: "💪", study: "📚", mindfulness: "🧘" };
const DAY_LABELS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
const MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
                "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"];

// ── Yardımcılar ─────────────────────────────────────
function escape(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

function isoDate(d) {
  return d.toISOString().slice(0, 10);
}

function todayIso() {
  return isoDate(new Date());
}

function formatDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${d.getDate()} ${MONTHS[d.getMonth()]}`;
}

// Son 7 günün (Pzt başlangıçlı değil; bugünden geriye) done durumu
function weekStrip(doneDates) {
  const cells = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const iso = isoDate(d);
    cells.push({
      iso,
      label: DAY_LABELS[(d.getDay() + 6) % 7],
      done: doneDates.has(iso),
      isToday: iso === todayIso(),
    });
  }
  return cells;
}

// ── Greeting ────────────────────────────────────────
(function greet() {
  const h = new Date().getHours();
  const msg = h < 6 ? "iyi geceler" : h < 12 ? "günaydın" : h < 18 ? "iyi günler" : "iyi akşamlar";
  document.getElementById("greeting").textContent = msg;
})();

logoutBtn.addEventListener("click", () => {
  window.auth.clearToken();
  window.location.href = "/";
});

toggleAdd.addEventListener("click", () => {
  form.hidden = !form.hidden;
  toggleAdd.textContent = form.hidden ? "＋ Yeni Alışkanlık Ekle" : "× Kapat";
  if (!form.hidden) document.getElementById("habit-name").focus();
});

// ── Modal (Bugünü Tamamla) ──────────────────────────
const modal = document.getElementById("checkin-modal");
const modalSub = document.getElementById("modal-sub");
const modalStatus = document.getElementById("modal-status");
const checkinForm = document.getElementById("checkin-form");
const checkinNote = document.getElementById("checkin-note");
const checkinPhoto = document.getElementById("checkin-photo");
const checkinSubmit = document.getElementById("checkin-submit");
let activeHabitId = null;

function openModal(habit, existingLog) {
  activeHabitId = habit.id;
  modalSub.textContent = `${habit.name} · ${formatDate(todayIso())}`;
  checkinNote.value = existingLog?.notes || "";
  checkinPhoto.value = "";
  modalStatus.textContent = "";
  modalStatus.className = "modal-status";
  modal.hidden = false;
}

function closeModal() {
  modal.hidden = true;
  activeHabitId = null;
}

document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal-cancel").addEventListener("click", closeModal);
modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

checkinForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!activeHabitId) return;
  checkinSubmit.disabled = true;
  checkinSubmit.textContent = "Kaydediliyor...";
  const note = checkinNote.value.trim() || null;
  const file = checkinPhoto.files[0];
  try {
    await window.api.trackHabit(activeHabitId, { done: true, notes: note, log_date: todayIso() });
    if (file) {
      modalStatus.textContent = "Fotoğraf yükleniyor...";
      modalStatus.className = "modal-status uploading";
      await window.api.uploadPhoto(activeHabitId, file, todayIso());
    }
    closeModal();
    await loadHabits();
  } catch (err) {
    modalStatus.textContent = "Hata: " + err.message;
    modalStatus.className = "modal-status error";
  } finally {
    checkinSubmit.disabled = false;
    checkinSubmit.textContent = "Tamamla ✓";
  }
});

// ── Liste yükleme ───────────────────────────────────
async function loadHabits() {
  listEl.innerHTML = '<p class="loading">Yükleniyor...</p>';
  try {
    const habits = await window.api.listHabits();
    if (habits.length === 0) {
      listEl.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">🌱</div>
          <p>Henüz alışkanlık yok.</p>
          <p class="empty-sub">Yukarıdan ilk alışkanlığını ekle, yolculuk başlasın.</p>
        </div>`;
      updateStats([]);
      return;
    }

    const enriched = await Promise.all(habits.map(async (h) => {
      const logs = await window.api.getLogs(h.id).catch(() => []);
      return { ...h, logs };
    }));

    updateStats(enriched);
    listEl.innerHTML = enriched.map(renderHabit).join("");
    attachHandlers(enriched);
  } catch (err) {
    listEl.innerHTML = `<p class="error">${escape(err.message)}</p>`;
  }
}

// Streak: bugünden (veya dünden) geriye kesintisiz done günleri
function computeStreak(doneDates) {
  let streak = 0;
  const start = new Date();
  // Bugün yapılmadıysa dünden saymaya başla
  if (!doneDates.has(todayIso())) start.setDate(start.getDate() - 1);
  for (let i = 0; ; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() - i);
    if (doneDates.has(isoDate(d))) streak++;
    else break;
  }
  return streak;
}

function updateStats(habits) {
  let today = 0, longest = 0;
  for (const h of habits) {
    const done = new Set((h.logs || []).filter(l => l.done).map(l => l.log_date));
    if (done.has(todayIso())) today++;
    longest = Math.max(longest, computeStreak(done));
  }
  document.getElementById("stat-total").textContent = habits.length;
  document.getElementById("stat-today").textContent = today;
  document.getElementById("stat-streak").textContent = longest;
}

function renderHabit(h) {
  const done = new Set((h.logs || []).filter(l => l.done).map(l => l.log_date));
  const streak = computeStreak(done);
  const doneToday = done.has(todayIso());
  const cells = weekStrip(done).map(c => `
    <div class="day-cell ${c.done ? 'done' : ''} ${c.isToday ? 'today' : ''}" title="${c.iso}">
      <span class="day-dot"></span>
      <span class="day-label">${c.label}</span>
    </div>`).join("");

  const cat = h.category ? `<span class="badge">${CATEGORY_EMOJI[h.category] || "📌"} ${escape(h.category)}</span>` : "";

  return `
    <div class="habit-item" data-id="${h.id}">
      <div class="habit-header">
        <div class="habit-title">
          <h3>${escape(h.name)}</h3>
          ${h.description ? `<p>${escape(h.description)}</p>` : ""}
          <div class="habit-meta">
            ${cat}
            <span class="badge">🎯 ${h.goal_days_per_week} gün/hafta</span>
          </div>
        </div>
        <div class="habit-streak">
          <span class="streak-num ${streak > 0 ? 'active' : ''}">🔥 ${streak}</span>
          <span class="streak-label">günlük seri</span>
        </div>
      </div>

      <div class="week-strip">${cells}</div>

      <div class="habit-footer">
        <div class="footer-left">
          <button class="btn-history" data-history="${h.id}">📅 Geçmiş (${(h.logs || []).length})</button>
          <button class="btn-delete" data-delete="${h.id}" title="Sil">🗑</button>
        </div>
        <button class="btn-track ${doneToday ? 'completed' : ''}" data-track="${h.id}">
          ${doneToday ? "✓ Bugün Tamamlandı" : "✓ Bugünü Tamamla"}
        </button>
      </div>

      <div class="history-panel" data-history-panel="${h.id}" hidden></div>
    </div>`;
}

function renderHistory(logs) {
  if (!logs.length) return '<p class="empty-sub">Henüz kayıt yok.</p>';
  return `<ul class="log-list">` + logs.map(l => `
    <li class="log-item">
      <span class="log-date">📅 ${formatDate(l.log_date)}</span>
      <span class="log-done">${l.done ? "✓" : "—"}</span>
      ${l.photo_key ? '<span class="log-photo" title="Fotoğraf var">📷</span>' : ""}
      ${l.notes ? `<span class="log-note">${escape(l.notes)}</span>` : ""}
    </li>`).join("") + `</ul>`;
}

function attachHandlers(habits) {
  const byId = Object.fromEntries(habits.map(h => [String(h.id), h]));

  listEl.querySelectorAll("[data-track]").forEach(btn => {
    btn.addEventListener("click", () => {
      const h = byId[btn.dataset.track];
      const todayLog = (h.logs || []).find(l => l.log_date === todayIso());
      openModal(h, todayLog);
    });
  });

  listEl.querySelectorAll("[data-history]").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.history;
      const panel = listEl.querySelector(`[data-history-panel="${id}"]`);
      if (panel.hidden) {
        panel.innerHTML = renderHistory(byId[id].logs || []);
        panel.hidden = false;
      } else {
        panel.hidden = true;
      }
    });
  });

  listEl.querySelectorAll("[data-delete]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.delete;
      const h = byId[id];
      if (!confirm(`"${h.name}" alışkanlığını silmek istediğine emin misin?`)) return;
      btn.disabled = true;
      try {
        await window.api.deleteHabit(id);
        await loadHabits();
      } catch (err) {
        alert("Silinemedi: " + err.message);
        btn.disabled = false;
      }
    });
  });
}

// ── Yeni alışkanlık ─────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  newError.hidden = true;
  createBtn.disabled = true;
  createBtn.textContent = "Ekleniyor...";
  const payload = {
    name: document.getElementById("habit-name").value.trim(),
    description: document.getElementById("habit-description").value.trim() || null,
    category: document.getElementById("habit-category").value,
    goal_days_per_week: parseInt(document.getElementById("habit-goal").value, 10),
  };
  try {
    await window.api.createHabit(payload);
    form.reset();
    document.getElementById("habit-goal").value = "7";
    form.hidden = true;
    toggleAdd.textContent = "＋ Yeni Alışkanlık Ekle";
    await loadHabits();
  } catch (err) {
    newError.textContent = err.message;
    newError.hidden = false;
  } finally {
    createBtn.disabled = false;
    createBtn.textContent = "Ekle";
  }
});

loadHabits();
