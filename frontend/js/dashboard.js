if (!window.auth.requireAuth()) {
  throw new Error("Redirecting to login");
}

const listEl = document.getElementById("habits-list");
const todaySection = document.getElementById("today-section");
const todaySummary = document.getElementById("today-summary");
const todayCount = document.getElementById("today-count");
const allCount = document.getElementById("all-count");
const form = document.getElementById("new-habit-form");
const newError = document.getElementById("new-habit-error");
const createBtn = document.getElementById("create-habit-btn");
const logoutBtn = document.getElementById("logout-btn");
const toggleAdd = document.getElementById("toggle-add");

const CATEGORY_EMOJI = { health: "🏥", fitness: "💪", study: "📚", mindfulness: "🧘" };
const DAY_LABELS = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"];
const MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
                "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"];

let objectUrls = [];

// ── Yardımcılar ─────────────────────────────────────
function escape(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function isoDate(d) { return d.toISOString().slice(0, 10); }
function todayIso() { return isoDate(new Date()); }
function formatDate(iso) {
  const d = new Date(iso + "T00:00:00");
  return `${d.getDate()} ${MONTHS[d.getMonth()]}`;
}
function doneSet(logs) {
  return new Set((logs || []).filter(l => l.done).map(l => l.log_date));
}
function todayLogOf(h) {
  return (h.logs || []).find(l => l.log_date === todayIso());
}

function currentStreak(done) {
  let s = 0;
  const start = new Date();
  if (!done.has(todayIso())) start.setDate(start.getDate() - 1);
  for (let i = 0; ; i++) {
    const d = new Date(start); d.setDate(d.getDate() - i);
    if (done.has(isoDate(d))) s++; else break;
  }
  return s;
}
function longestStreak(done) {
  if (done.size === 0) return 0;
  const days = [...done].sort();
  let best = 1, run = 1;
  for (let i = 1; i < days.length; i++) {
    const diff = Math.round(
      (new Date(days[i] + "T00:00:00") - new Date(days[i - 1] + "T00:00:00")) / 86400000);
    run = diff === 1 ? run + 1 : 1;
    best = Math.max(best, run);
  }
  return best;
}
function weeklyCount(done) {
  let n = 0;
  for (let i = 0; i < 7; i++) {
    const d = new Date(); d.setDate(d.getDate() - i);
    if (done.has(isoDate(d))) n++;
  }
  return n;
}
function motivation(streak) {
  if (streak === 0) return "🌱 Bugün başla, ilk adımı at!";
  if (streak < 3) return `💪 ${streak} gün — güzel başlangıç, devam!`;
  if (streak < 7) return `🔥 ${streak} gün! Momentum yakaladın.`;
  if (streak < 21) return `🌟 ${streak} gün! Alışkanlık oturuyor.`;
  return `🏆 ${streak} gün! Efsanesin, bırakma!`;
}
function weekStrip(done) {
  const cells = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(); d.setDate(d.getDate() - i);
    const iso = isoDate(d);
    cells.push({
      label: DAY_LABELS[(d.getDay() + 6) % 7],
      done: done.has(iso),
      isToday: iso === todayIso(),
    });
  }
  return cells;
}

// ── Konfeti ─────────────────────────────────────────
function celebrate() {
  const colors = ["#4f46e5", "#16a34a", "#f59e0b", "#dc2626", "#2980b9", "#e67e22"];
  for (let i = 0; i < 28; i++) {
    const c = document.createElement("div");
    c.className = "confetti";
    c.style.left = Math.random() * 100 + "vw";
    c.style.background = colors[i % colors.length];
    c.style.animationDelay = Math.random() * 0.25 + "s";
    document.body.appendChild(c);
    setTimeout(() => c.remove(), 1600);
  }
}

// ── Greeting ────────────────────────────────────────
(function greet() {
  const h = new Date().getHours();
  document.getElementById("greeting").textContent =
    h < 6 ? "iyi geceler" : h < 12 ? "günaydın" : h < 18 ? "iyi günler" : "iyi akşamlar";
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

// ── Modal + mood ────────────────────────────────────
const modal = document.getElementById("checkin-modal");
const modalSub = document.getElementById("modal-sub");
const modalStatus = document.getElementById("modal-status");
const checkinForm = document.getElementById("checkin-form");
const checkinNote = document.getElementById("checkin-note");
const checkinPhoto = document.getElementById("checkin-photo");
const checkinSubmit = document.getElementById("checkin-submit");
const moodPicker = document.getElementById("mood-picker");
let activeHabitId = null;
let lastFocused = null;
let selectedMood = null;

moodPicker.querySelectorAll(".mood-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const m = btn.dataset.mood;
    if (selectedMood === m) {           // tekrar tıkla → seçimi kaldır
      selectedMood = null;
      btn.classList.remove("selected");
    } else {
      selectedMood = m;
      moodPicker.querySelectorAll(".mood-btn").forEach(b => b.classList.remove("selected"));
      btn.classList.add("selected");
    }
  });
});

function openModal(habit, existingLog) {
  activeHabitId = habit.id;
  lastFocused = document.activeElement;
  modalSub.textContent = `${habit.name} · ${formatDate(todayIso())}`;
  checkinNote.value = existingLog?.notes || "";
  selectedMood = existingLog?.mood || null;
  moodPicker.querySelectorAll(".mood-btn").forEach(b =>
    b.classList.toggle("selected", b.dataset.mood === selectedMood));
  checkinPhoto.value = "";
  modalStatus.textContent = "";
  modalStatus.className = "modal-status";
  modal.hidden = false;
  setTimeout(() => checkinNote.focus(), 50);
}
function closeModal() {
  modal.hidden = true;
  activeHabitId = null;
  if (lastFocused) lastFocused.focus();
}
document.getElementById("modal-close").addEventListener("click", closeModal);
document.getElementById("modal-cancel").addEventListener("click", closeModal);
modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) closeModal();
});

checkinForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (!activeHabitId) return;
  checkinSubmit.disabled = true;
  checkinSubmit.textContent = "Kaydediliyor...";
  const note = checkinNote.value.trim() || null;
  const file = checkinPhoto.files[0];
  try {
    await window.api.trackHabit(activeHabitId,
      { done: true, notes: note, mood: selectedMood, log_date: todayIso() });
    if (file) {
      modalStatus.textContent = "Fotoğraf yükleniyor...";
      modalStatus.className = "modal-status uploading";
      await window.api.uploadPhoto(activeHabitId, file, todayIso());
    }
    closeModal();
    celebrate();
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
  objectUrls.forEach(URL.revokeObjectURL);
  objectUrls = [];
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
      todaySection.hidden = true;
      updateStats([]);
      return;
    }
    const enriched = await Promise.all(habits.map(async (h) => {
      const logs = await window.api.getLogs(h.id).catch(() => []);
      return { ...h, logs };
    }));

    updateStats(enriched);

    // ── Bugün takip edilenler (özet) ──
    const doneToday = enriched.filter(h => doneSet(h.logs).has(todayIso()));
    if (doneToday.length) {
      todaySection.hidden = false;
      todayCount.textContent = doneToday.length;
      todaySummary.innerHTML = doneToday.map(h => {
        const log = todayLogOf(h);
        const streak = currentStreak(doneSet(h.logs));
        return `
          <div class="today-chip">
            <span class="chip-mood">${log?.mood || "✓"}</span>
            <span class="chip-name">${escape(h.name)}</span>
            <span class="chip-streak">🔥${streak}</span>
          </div>`;
      }).join("");
    } else {
      todaySection.hidden = true;
    }

    // ── Tüm alışkanlıklar (yapılmayanlar üstte) ──
    enriched.sort((a, b) => {
      const ad = doneSet(a.logs).has(todayIso()) ? 1 : 0;
      const bd = doneSet(b.logs).has(todayIso()) ? 1 : 0;
      return ad - bd;
    });
    allCount.textContent = enriched.length;
    listEl.innerHTML = enriched.map(renderHabit).join("");
    attachHandlers(enriched);
  } catch (err) {
    listEl.innerHTML = `<p class="error">${escape(err.message)}</p>`;
  }
}

function updateStats(habits) {
  let today = 0, longest = 0;
  for (const h of habits) {
    const done = doneSet(h.logs);
    if (done.has(todayIso())) today++;
    longest = Math.max(longest, longestStreak(done));
  }
  document.getElementById("stat-total").textContent = habits.length;
  document.getElementById("stat-today").textContent = `${today}/${habits.length}`;
  document.getElementById("stat-streak").textContent = longest;
}

function renderHabit(h) {
  const done = doneSet(h.logs);
  const streak = currentStreak(done);
  const best = longestStreak(done);
  const total = done.size;
  const doneToday = done.has(todayIso());
  const week = weeklyCount(done);
  const goal = h.goal_days_per_week;
  const pct = Math.min(100, Math.round((week / goal) * 100));
  const tlog = todayLogOf(h);

  const cells = weekStrip(done).map(c => `
    <div class="day-cell ${c.done ? 'done' : ''} ${c.isToday ? 'today' : ''}">
      <span class="day-dot"></span><span class="day-label">${c.label}</span>
    </div>`).join("");

  const cat = h.category
    ? `<span class="badge">${CATEGORY_EMOJI[h.category] || "📌"} ${escape(h.category)}</span>` : "";

  return `
    <div class="habit-item ${doneToday ? 'is-done' : ''}" data-id="${h.id}">
      <div class="habit-header">
        <div class="habit-title">
          <h3>${escape(h.name)} ${doneToday && tlog?.mood ? `<span class="title-mood">${tlog.mood}</span>` : ""}</h3>
          ${h.description ? `<p>${escape(h.description)}</p>` : ""}
          <div class="habit-meta">
            ${cat}
            <span class="badge">🎯 ${goal}/hafta</span>
            <span class="badge">🏆 en iyi: ${best}</span>
            <span class="badge">✅ toplam: ${total}</span>
          </div>
        </div>
        <div class="habit-streak">
          <span class="streak-num ${streak > 0 ? 'active' : 'zero'}">${streak > 0 ? '🔥' : '·'} ${streak}</span>
          <span class="streak-label">günlük seri</span>
        </div>
      </div>

      <div class="progress-row">
        <div class="progress-track"><div class="progress-fill" style="width:${pct}%"></div></div>
        <span class="progress-text">Bu hafta ${week}/${goal}</span>
      </div>

      <div class="week-strip">${cells}</div>

      <p class="motivation">${motivation(streak)}</p>

      <div class="habit-footer">
        <div class="footer-left">
          <button class="btn-history" data-history="${h.id}">📅 Geçmiş (${(h.logs || []).length})</button>
          <button class="btn-delete" data-delete="${h.id}" title="Sil">🗑</button>
        </div>
        <button class="btn-track ${doneToday ? 'completed' : ''}" data-track="${h.id}" data-done="${doneToday}">
          ${doneToday ? "✓ Tamamlandı (geri al)" : "✓ Bugünü Tamamla"}
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
      ${l.mood ? `<span class="log-mood">${l.mood}</span>` : ""}
      ${l.photo_key ? `<button class="log-photo" data-photo-key="${escape(l.photo_key)}" title="Fotoğrafı gör">📷 Gör</button>` : ""}
      ${l.notes ? `<span class="log-note">${escape(l.notes)}</span>` : ""}
    </li>`).join("") + `</ul>`;
}

function attachHandlers(habits) {
  const byId = Object.fromEntries(habits.map(h => [String(h.id), h]));

  listEl.querySelectorAll("[data-track]").forEach(btn => {
    btn.addEventListener("click", async () => {
      const h = byId[btn.dataset.track];
      if (btn.dataset.done === "true") {
        if (!confirm(`"${h.name}" için bugünkü tamamlamayı geri al?`)) return;
        btn.disabled = true;
        try {
          await window.api.trackHabit(h.id, { done: false, log_date: todayIso() });
          await loadHabits();
        } catch (err) { alert("Hata: " + err.message); btn.disabled = false; }
      } else {
        openModal(h, todayLogOf(h));
      }
    });
  });

  listEl.querySelectorAll("[data-history]").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.history;
      const panel = listEl.querySelector(`[data-history-panel="${id}"]`);
      if (panel.hidden) {
        panel.innerHTML = renderHistory(byId[id].logs || []);
        panel.hidden = false;
        panel.querySelectorAll("[data-photo-key]").forEach(el => {
          el.addEventListener("click", async () => {
            if (el.dataset.loaded) {
              const img = el.parentElement.querySelector(".log-photo-img");
              if (img) img.style.display = img.style.display === "none" ? "block" : "none";
              return;
            }
            el.textContent = "📷 yükleniyor...";
            try {
              const url = await window.api.photoUrl(id, el.dataset.photoKey);
              objectUrls.push(url);
              const img = document.createElement("img");
              img.src = url; img.className = "log-photo-img";
              el.parentElement.appendChild(img);
              el.dataset.loaded = "1";
              el.textContent = "📷 gizle/göster";
            } catch (err) { el.textContent = "📷 hata"; }
          });
        });
      } else { panel.hidden = true; }
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
      } catch (err) { alert("Silinemedi: " + err.message); btn.disabled = false; }
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
