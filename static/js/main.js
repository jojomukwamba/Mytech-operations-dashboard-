/* FTP Ops – main.js */
'use strict';

// ── Sidebar toggle ────────────────────────────────────────────────────────────
const toggleBtn = document.getElementById('sidebarToggle');
const sidebar   = document.getElementById('sidebar');

if (toggleBtn && sidebar) {
  toggleBtn.addEventListener('click', () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle('mobile-open');
    } else {
      sidebar.classList.toggle('collapsed');
    }
  });
}

// ── Auto-dismiss alerts after 4 s ────────────────────────────────────────────
document.querySelectorAll('.alert').forEach(el => {
  setTimeout(() => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    bsAlert.close();
  }, 4000);
});
