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

    const categoryEmoji = { health: "🏥", fitness: "💪", study: "📚", mindfulness: "🧘" };

    listEl.innerHTML = items.map(h => `
      <div class="habit-item" data-id="${h.id}">
        <div class="habit-header">
          <div class="habit-title">
            <h3>${escape(h.name)}</h3>
            ${h.description ? `<p>${escape(h.description)}</p>` : ""}
            <div class="habit-meta">
              ${h.category ? `<span class="badge">${categoryEmoji[h.category] || "📌"} ${escape(h.category)}</span>` : ""}
              <span class="badge">🎯 ${h.goal_days_per_week} gün/hafta</span>
            </div>
          </div>
          <span class="streak-badge ${h.streak > 0 ? 'active' : ''}">🔥 ${h.streak} gün</span>
        </div>
        <div class="habit-footer">
          <div class="photo-section">
            <label class="upload-label">
              📸 Fotoğraf Yükle
              <input type="file" data-upload="${h.id}" accept="image/*" hidden>
            </label>
            <button class="btn-secondary" data-photos="${h.id}">Listele</button>
            <div class="photo-status" data-status="${h.id}"></div>
            <ul class="photo-list" data-list="${h.id}" hidden></ul>
          </div>
          <button class="btn-track" data-track="${h.id}">✓ Bugün Yaptım</button>
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

    listEl.querySelectorAll("[data-upload]").forEach(input => {
      input.addEventListener("change", async (e) => {
        const id = input.dataset.upload;
        const file = e.target.files[0];
        if (!file) return;
        const status = listEl.querySelector(`[data-status="${id}"]`);
        status.textContent = "Yükleniyor...";
        status.className = "photo-status uploading";
        try {
          const res = await window.api.uploadPhoto(id, file);
          status.textContent = `✓ ${file.name} (${(res.size_bytes / 1024).toFixed(1)} KB) S3'e yüklendi`;
          status.className = "photo-status success";
        } catch (err) {
          status.textContent = `✗ ${err.message}`;
          status.className = "photo-status error";
        }
        input.value = "";
      });
    });

    listEl.querySelectorAll("[data-photos]").forEach(btn => {
      btn.addEventListener("click", async () => {
        const id = btn.dataset.photos;
        const ul = listEl.querySelector(`[data-list="${id}"]`);
        btn.disabled = true;
        try {
          const res = await window.api.listPhotos(id);
          if (res.count === 0) {
            ul.innerHTML = "<li class='empty'>Henüz fotoğraf yok.</li>";
          } else {
            ul.innerHTML = res.keys.map(k => `<li>📄 ${escape(k)}</li>`).join("");
          }
          ul.hidden = false;
        } catch (err) {
          ul.innerHTML = `<li class='error'>${escape(err.message)}</li>`;
          ul.hidden = false;
        } finally {
          btn.disabled = false;
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
