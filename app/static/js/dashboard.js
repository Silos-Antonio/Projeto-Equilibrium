document.querySelectorAll('[data-altura]').forEach((barra) => {
    barra.style.height = `${barra.dataset.altura}%`;

});

document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');

    if (menuToggle && navLinks) {
        menuToggle.addEventListener('click', (evento) => {
            // Impede que o clique suba para o documento e acione o fechamento
            evento.stopPropagation(); 
            
            navLinks.classList.toggle('active');
            console.log('Menu clicado! A classe active está:', navLinks.classList.contains('active'));
            
            const isOpen = navLinks.classList.contains('active');
            menuToggle.setAttribute('aria-expanded', isOpen);
        });

        document.addEventListener('click', (evento) => {
            if (!menuToggle.contains(evento.target) && !navLinks.contains(evento.target)) {
                navLinks.classList.remove('active');
                menuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    } else {
        console.error('Erro: Botão .menu-toggle ou .nav-links não encontrados.');
    }
});