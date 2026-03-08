/**
 * EmailIQ – Main JavaScript
 * Handles UI interactions and animations.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Animate confidence bars on load
  document.querySelectorAll(".conf-bar-fill").forEach(bar => {
    const target = bar.style.width;
    bar.style.width = "0%";
    setTimeout(() => { bar.style.width = target; }, 200);
  });

  // Auto-dismiss flash messages
  document.querySelectorAll(".flash").forEach(flash => {
    setTimeout(() => flash.remove(), 4000);
  });
});
