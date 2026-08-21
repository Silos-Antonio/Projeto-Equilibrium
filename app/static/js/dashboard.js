document.querySelectorAll('[data-altura]').forEach((barra) => {
    barra.style.height = `${barra.dataset.altura}%`;
});
