document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#chakra-form');
    if (!form) return;

    const inputs = [...form.querySelectorAll('[data-chakra-control]')];
    const map = document.querySelector('.chakra-figure');
    const confirmed = new Set();

    inputs.forEach((input) => {
        const id = input.dataset.chakraControl;
        const update = () => {
            const value = Number(input.value);
            input.style.setProperty('--range-progress', `${value}%`);
            const orb = map.querySelector(`[data-chakra="${id}"]`);
            orb.style.setProperty('--balance', value / 100);
            orb.classList.add('is-set');
            input.setAttribute('aria-valuetext', `${value}% de equilíbrio`);
            form.querySelector(`[data-percent="${id}"]`).textContent = `${value}%`;
            form.querySelector(`[data-state="${id}"]`).textContent = 'Nível definido';
            if (!confirmed.has(id)) {
                const marker = document.createElement('input');
                marker.type = 'hidden';
                marker.name = 'confirmado';
                marker.value = id;
                marker.dataset.marker = id;
                form.append(marker);
                confirmed.add(id);
            }
        };
        input.addEventListener('input', update);
        input.addEventListener('change', update);
    });

    form.addEventListener('submit', (event) => {
        if (confirmed.size !== inputs.length) {
            event.preventDefault();
            const firstUnset = inputs.find((input) => !confirmed.has(input.dataset.chakraControl));
            firstUnset?.focus();
            form.querySelector('.chakra-hint').textContent = 'Ajuste os sete controles para confirmar todos os níveis antes de salvar.';
            form.querySelector('.chakra-hint').setAttribute('role', 'alert');
        }
    });
});
