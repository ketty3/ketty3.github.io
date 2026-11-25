(function () {
  const slides = Array.from(document.querySelectorAll('.slide'));
  if (!slides.length) return;

  const counter = document.querySelector('[data-counter]');
  const bar = document.querySelector('.progress-bar');
  const prev = document.querySelector('[data-prev]');
  const next = document.querySelector('[data-next]');
  const dotsHost = document.querySelector('[data-dots]');
  let current = 0;

  slides.forEach((_, i) => {
    const dot = document.createElement('button');
    dot.className = 'dot-btn';
    dot.type = 'button';
    dot.setAttribute('aria-label', 'Слайд ' + (i + 1));
    dot.addEventListener('click', () => go(i));
    dotsHost.appendChild(dot);
  });
  const dots = Array.from(dotsHost.children);

  function go(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    slides.forEach((slide, i) => slide.classList.toggle('active', i === current));
    dots.forEach((dot, i) => dot.classList.toggle('current', i === current));
    if (counter) counter.textContent = String(current + 1).padStart(2, '0') + ' / ' + String(slides.length).padStart(2, '0');
    if (bar) bar.style.width = ((current + 1) / slides.length) * 100 + '%';
    if (prev) prev.disabled = current === 0;
    if (next) next.disabled = current === slides.length - 1;
    if (location.hash !== '#slide-' + (current + 1)) history.replaceState(null, '', '#slide-' + (current + 1));
  }

  if (prev) prev.addEventListener('click', () => go(current - 1));
  if (next) next.addEventListener('click', () => go(current + 1));

  document.addEventListener('keydown', (event) => {
    if (['ArrowRight', 'PageDown', ' '].includes(event.key)) {
      if (event.target && event.target.tagName === 'BUTTON' && event.key === ' ') return;
      event.preventDefault();
      go(current + 1);
    } else if (['ArrowLeft', 'PageUp'].includes(event.key)) {
      event.preventDefault();
      go(current - 1);
    } else if (event.key === 'Home') {
      go(0);
    } else if (event.key === 'End') {
      go(slides.length - 1);
    }
  });

  const fromHash = parseInt((location.hash || '').replace('#slide-', ''), 10);
  go(Number.isFinite(fromHash) ? fromHash - 1 : 0);
})();
