document.addEventListener('DOMContentLoaded', () => {
  const downObjects = document.querySelectorAll('.Down');

  downObjects.forEach(down => {
    const computedTop = window.getComputedStyle(down).top;
    const offset = parseFloat(computedTop) || 0;

    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY * 1.2;
      down.style.top = `${offset + scrollY}px`;
    });
  });
});