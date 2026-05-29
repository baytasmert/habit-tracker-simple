// Backend REST API ile konuşan yardımcı katman.

function getToken() {
  return localStorage.getItem(window.TOKEN_KEY);
}

function setToken(t) {
  localStorage.setItem(window.TOKEN_KEY, t);
}

function clearToken() {
  localStorage.removeItem(window.TOKEN_KEY);
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/";
    return false;
  }
  return true;
}

async function apiCall(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${window.API_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth) {
    clearToken();
    window.location.href = "/login.html";
    throw new Error("Unauthorized");
  }

  const data = res.status === 204 ? null : await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.detail || `İstek başarısız (${res.status})`;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

async function uploadFile(path, file, extraFields = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const fd = new FormData();
  fd.append("file", file);
  for (const [k, v] of Object.entries(extraFields)) fd.append(k, v);

  const res = await fetch(`${window.API_URL}${path}`, {
    method: "POST",
    headers,
    body: fd,
  });

  if (res.status === 401) {
    clearToken();
    window.location.href = "/login.html";
    throw new Error("Unauthorized");
  }

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data?.detail || `Upload başarısız (${res.status})`);
  }
  return data;
}

window.api = {
  register: (username, email, password) =>
    apiCall("/register", { method: "POST", body: { username, email, password }, auth: false }),
  login: (email, password) =>
    apiCall("/login", { method: "POST", body: { email, password }, auth: false }),
  listHabits: () => apiCall("/habits"),
  createHabit: (data) => apiCall("/habits", { method: "POST", body: data }),
  deleteHabit: (id) => apiCall(`/habits/${id}`, { method: "DELETE" }),
  trackHabit: (id, { done = true, notes = null, mood = null, log_date = null } = {}) =>
    apiCall(`/habits/${id}/track`, { method: "POST", body: { done, notes, mood, log_date } }),
  getStreak: (id) => apiCall(`/habits/${id}/streak`),
  getLogs: (id) => apiCall(`/habits/${id}/logs`),
  uploadPhoto: (id, file, logDate = null) =>
    uploadFile(`/habits/${id}/photo`, file, logDate ? { log_date: logDate } : {}),
  listPhotos: (id) => apiCall(`/habits/${id}/photos`),
  photoUrl: async (id, key) => {
    const headers = {};
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const res = await fetch(
      `${window.API_URL}/habits/${id}/photo-file?key=${encodeURIComponent(key)}`,
      { headers }
    );
    if (!res.ok) throw new Error("Fotoğraf yüklenemedi");
    return URL.createObjectURL(await res.blob());
  },
};

window.auth = { getToken, setToken, clearToken, requireAuth };
