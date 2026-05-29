if (window.auth.getToken()) {
  window.location.href = "/dashboard.html";
}

const form = document.getElementById("login-form");
const errorEl = document.getElementById("error");
const btn = document.getElementById("login-btn");

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.hidden = true;
  btn.disabled = true;
  btn.textContent = "Giriş yapılıyor...";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const data = await window.api.login(email, password);
    window.auth.setToken(data.access_token);
    window.location.href = "/dashboard.html";
  } catch (err) {
    showError(err.message);
    btn.disabled = false;
    btn.textContent = "Giriş Yap";
  }
});
