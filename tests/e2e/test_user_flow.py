"""
E2E testleri — gerçek tarayıcı, gerçek frontend + backend.

Çalıştırmak için:
    docker-compose up -d
    playwright install chromium
    pytest tests/e2e/ -v

Frontend: http://localhost:8080  (NGINX)
Backend:  http://localhost:8000  (FastAPI)
"""
import time
import uuid

import pytest
from playwright.sync_api import Page, expect


FRONTEND_URL = "http://localhost:8080"


def _unique_user():
    rnd = uuid.uuid4().hex[:8]
    return {
        "username": f"e2e_{rnd}",
        "email": f"e2e_{rnd}@x.com",
        "password": "secret123",
    }


def test_register_login_dashboard_flow(page: Page):
    """Senaryo 1: Yeni kullanıcı kayıt olur, dashboard'a yönlenir."""
    user = _unique_user()

    page.goto(f"{FRONTEND_URL}/register.html")
    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#password", user["password"])
    page.click("#register-btn")

    page.wait_for_url(f"{FRONTEND_URL}/dashboard.html", timeout=10000)
    expect(page.locator("h1")).to_contain_text("Habit Tracker")


def test_login_with_invalid_password_shows_error(page: Page):
    """Senaryo 2: Yanlış şifre giren kullanıcıya hata mesajı gösterilir."""
    page.goto(f"{FRONTEND_URL}/login.html")
    page.fill("#email", "doesnotexist@x.com")
    page.fill("#password", "wrongpassword")
    page.click("#login-btn")

    error = page.locator("#error")
    expect(error).to_be_visible(timeout=5000)
    expect(error).not_to_be_empty()


def test_welcome_page_shows_cta_buttons(page: Page):
    """Senaryo 6: Ana sayfa karşılama, login + register CTA'ları görünür."""
    page.goto(f"{FRONTEND_URL}/")
    expect(page.locator("h1")).to_contain_text("Küçük alışkanlıklar")
    expect(page.locator(".btn-primary")).to_be_visible()
    expect(page.locator(".btn-ghost")).to_be_visible()


def test_create_habit_and_see_in_list(page: Page):
    """Senaryo 3: Login → habit oluştur → listede gör."""
    user = _unique_user()

    page.goto(f"{FRONTEND_URL}/register.html")
    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#password", user["password"])
    page.click("#register-btn")
    page.wait_for_url(f"{FRONTEND_URL}/dashboard.html")

    # Form toggle arkasında — önce aç
    page.click("#toggle-add")
    page.fill("#habit-name", "E2E test habit")
    page.fill("#habit-description", "Created via Playwright")
    page.click("#create-habit-btn")

    expect(page.locator(".habit-item h3").filter(has_text="E2E test habit")).to_be_visible(timeout=5000)


def test_track_habit_increments_streak(page: Page):
    """Senaryo 4: Habit oluştur, modal'dan tamamla, streak 1'e yükselsin."""
    user = _unique_user()

    page.goto(f"{FRONTEND_URL}/register.html")
    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#password", user["password"])
    page.click("#register-btn")
    page.wait_for_url(f"{FRONTEND_URL}/dashboard.html")

    page.click("#toggle-add")
    page.fill("#habit-name", "Daily meditation")
    page.click("#create-habit-btn")

    # "Bugünü Tamamla" → modal açılır
    track_btn = page.locator("[data-track]").first
    expect(track_btn).to_be_visible(timeout=5000)
    track_btn.click()

    # Modal'da not gir, tamamla
    expect(page.locator("#checkin-modal")).to_be_visible(timeout=5000)
    page.fill("#checkin-note", "Playwright E2E notu")
    page.click("#checkin-submit")

    # Streak sayısı 1 olmalı
    streak = page.locator(".streak-num").first
    expect(streak).to_contain_text("1", timeout=5000)


def test_logout_redirects_to_login(page: Page):
    """Senaryo 5: Logout butonu kullanıcıyı login sayfasına yönlendirir, token silinir."""
    user = _unique_user()

    page.goto(f"{FRONTEND_URL}/register.html")
    page.fill("#username", user["username"])
    page.fill("#email", user["email"])
    page.fill("#password", user["password"])
    page.click("#register-btn")
    page.wait_for_url(f"{FRONTEND_URL}/dashboard.html")

    page.click("#logout-btn")
    page.wait_for_url(f"{FRONTEND_URL}/", timeout=5000)
    # Logout sonrası welcome sayfası — login formu değil, CTA butonları görünür
    expect(page.locator(".btn-primary")).to_be_visible()
