document.addEventListener('DOMContentLoaded', () => {
    const image = document.querySelector('.BrowingImage');

    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                image.classList.add('visible');
            }
        });
    });

    observer.observe(image);
});