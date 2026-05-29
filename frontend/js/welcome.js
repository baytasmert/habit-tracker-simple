// Eğer kullanıcı zaten giriş yapmışsa direkt dashboard'a yönlendir.
if (localStorage.getItem(window.TOKEN_KEY)) {
  window.location.href = "/dashboard.html";
}
