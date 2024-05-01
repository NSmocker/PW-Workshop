document.getElementById('toggleBtn').addEventListener('click', function() {
  var sidebar = document.getElementById('sidebar');
  if (sidebar.style.left === '-200px') {
    sidebar.style.left = '0';
  } else {
    sidebar.style.left = '-200px';
  }
});