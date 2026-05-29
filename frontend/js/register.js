const form = document.getElementById("register-form");
const errorEl = document.getElementById("error");
const btn = document.getElementById("register-btn");

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.hidden = false;
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.hidden = true;
  btn.disabled = true;
  btn.textContent = "Kaydediliyor...";

  const username = document.getElementById("username").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    await window.api.register(username, email, password);
    const data = await window.api.login(email, password);
    window.auth.setToken(data.access_token);
    window.location.href = "/dashboard.html";
  } catch (err) {
    showError(err.message);
    btn.disabled = false;
    btn.textContent = "Kayıt Ol";
  }
});
