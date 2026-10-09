/**
 * SheShield — Core Frontend Logic
 * Accessible navigation, quick safety exit, and interaction helpers.
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Mobile Navigation Toggle
  const navToggleBtn = document.getElementById("navToggleBtn");
  const navLinks = document.getElementById("navLinks");
  if (navToggleBtn && navLinks) {
    navToggleBtn.addEventListener("click", () => {
      const isExpanded = navToggleBtn.getAttribute("aria-expanded") === "true";
      navToggleBtn.setAttribute("aria-expanded", !isExpanded);
      navLinks.classList.toggle("active");
    });
  }

  // 2. Quick Exit (Safety Panic Redirection)
  // Replaces current history entry so hitting back button won't return to the page immediately
  const quickExitButtons = document.querySelectorAll(".quick-exit-btn");
  quickExitButtons.forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      window.location.replace("https://www.google.com");
    });
  });

  // ESC key quick exit shortcut (Press ESC 3 times quickly for emergency redirect)
  let escPressCount = 0;
  let escTimer = null;
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      escPressCount++;
      clearTimeout(escTimer);
      if (escPressCount >= 3) {
        window.location.replace("https://www.google.com");
      }
      escTimer = setTimeout(() => {
        escPressCount = 0;
      }, 1000);
    }
  });

  // 3. Dismissible Flash Messages
  const flashCloseButtons = document.querySelectorAll(".flash-close-btn");
  flashCloseButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const alert = btn.closest(".flash-alert");
      if (alert) {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 200);
      }
    });
  });
});

/**
 * Helper to fetch CSRF token from meta tag for AJAX requests
 */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}
