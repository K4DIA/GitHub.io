const internalLinks = document.querySelectorAll('a[href^="#"]');
const header = document.querySelector('.site-header');
const menuToggle = document.querySelector('.menu-toggle');

function closeMenu() {
  header.classList.remove('menu-open');
  menuToggle.setAttribute('aria-expanded', 'false');
  menuToggle.setAttribute('aria-label', 'Open site menu');
}

menuToggle.addEventListener('click', () => {
  const willOpen = !header.classList.contains('menu-open');
  header.classList.toggle('menu-open', willOpen);
  menuToggle.setAttribute('aria-expanded', String(willOpen));
  menuToggle.setAttribute('aria-label', willOpen ? 'Close site menu' : 'Open site menu');
});

internalLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    const targetId = link.getAttribute('href');
    if (targetId === '#') {
      event.preventDefault();
    } else {
      closeMenu();
    }
  });
});

document.addEventListener('click', (event) => {
  if (!header.contains(event.target)) closeMenu();
});

document.addEventListener('keydown', (event) => {
  if (event.key === 'Escape') closeMenu();
});
