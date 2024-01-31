document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.getElementById('sidebar');
  const toggleButton = document.getElementById('toggle-sidebar');

  toggleButton.addEventListener('click', function() {
    const sidebarWidth = parseInt(window.getComputedStyle(sidebar).width);
    const isSidebarHidden = sidebar.style.left === '-250px';

    sidebar.style.left = isSidebarHidden ? '0' : `-${sidebarWidth}px`;
  });
});
