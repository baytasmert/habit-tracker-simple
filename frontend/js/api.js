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

async function uploadFile(path, file) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const fd = new FormData();
  fd.append("file", file);

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
  trackHabit: (id, done = true, notes = null) =>
    apiCall(`/habits/${id}/track`, { method: "POST", body: { done, notes } }),
  getStreak: (id) => apiCall(`/habits/${id}/streak`),
  uploadPhoto: (id, file) => uploadFile(`/habits/${id}/photo`, file),
  listPhotos: (id) => apiCall(`/habits/${id}/photos`),
};

window.auth = { getToken, setToken, clearToken, requireAuth };
