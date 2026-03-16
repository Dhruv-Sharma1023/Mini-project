document.addEventListener("DOMContentLoaded", () => {
  // Confidence bar animations
  document.querySelectorAll(".conf-bar-fill").forEach(bar => {
    const w = bar.style.width; bar.style.width = "0%";
    setTimeout(() => { bar.style.width = w; }, 200);
  });
  // Auto-dismiss flash messages
  document.querySelectorAll(".flash").forEach(f => setTimeout(() => f.remove(), 5000));
});

// User dropdown toggle
function toggleUserMenu() {
  document.getElementById("userDropdown")?.classList.toggle("open");
}
document.addEventListener("click", e => {
  if (!e.target.closest(".user-menu"))
    document.getElementById("userDropdown")?.classList.remove("open");
});
