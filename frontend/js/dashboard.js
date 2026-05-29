if (!window.auth.requireAuth()) {
  throw new Error("Redirecting to login");
}

const listEl = document.getElementById("habits-list");
const form = document.getElementById("new-habit-form");
const newError = document.getElementById("new-habit-error");
const createBtn = document.getElementById("create-habit-btn");
const logoutBtn = document.getElementById("logout-btn");

logoutBtn.addEventListener("click", () => {
  window.auth.clearToken();
  window.location.href = "/";
});

function escape(s) {
  return String(s ?? "")
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

async function loadHabits() {
  listEl.innerHTML = '<p class="loading">Yükleniyor...</p>';
  try {
    const habits = await window.api.listHabits();
    if (habits.length === 0) {
      listEl.innerHTML = '<p class="empty">Henüz alışkanlık eklemedin. Yukarıdaki formdan başla.</p>';
      return;
    }

    const items = await Promise.all(habits.map(async (h) => {
      let streak = 0;
      try {
        const s = await window.api.getStreak(h.id);
        streak = s.current_streak;
      } catch (_) { /* ignore */ }
      return { ...h, streak };
    }));

    listEl.innerHTML = items.map(h => `
      <div class="habit-item" data-id="${h.id}">
        <div class="habit-info">
          <h3>${escape(h.name)}</h3>
          ${h.description ? `<p>${escape(h.description)}</p>` : ""}
          <div class="habit-meta">
            ${h.category ? `<span class="badge">${escape(h.category)}</span>` : ""}
            <span class="badge">Hedef: ${h.goal_days_per_week} gün/hafta</span>
          </div>
        </div>
        <span class="streak-badge">🔥 ${h.streak} gün</span>
        <div class="habit-actions">
          <button class="btn-track" data-track="${h.id}">Bugün Yaptım</button>
        </div>
      </div>
    `).join("");

    listEl.querySelectorAll("[data-track]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.track;
        btn.disabled = true;
        btn.textContent = "Kaydediliyor...";
        try {
          await window.api.trackHabit(id, true);
          await loadHabits();
        } catch (err) {
          alert("Hata: " + err.message);
          btn.disabled = false;
          btn.textContent = "Bugün Yaptım";
        }
      });
    });
  } catch (err) {
    listEl.innerHTML = `<p class="error">${escape(err.message)}</p>`;
  }
}

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
    await loadHabits();
  } catch (err) {
    newError.textContent = err.message;
    newError.hidden = false;
  } finally {
    createBtn.disabled = false;
    createBtn.textContent = "Oluştur";
  }
});

loadHabits();
