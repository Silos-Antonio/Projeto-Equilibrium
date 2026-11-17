const inicio = document.querySelector('#data_hora');
const duracao = document.querySelector('#duracao_minutos');
const fimPrevisto = document.querySelector('#fim-previsto');

const modalEditar = document.querySelector('#modal-editar');
const formEditar = document.querySelector('#form-editar');
const editDataHora = document.querySelector('#edit_data_hora');


function atualizarFimPrevisto() {
    if (!inicio || !duracao || !fimPrevisto) {
        return;
    }

    if (!inicio.value || !duracao.value) {
        fimPrevisto.textContent =
            'Escolha o horário para ver o término.';

        return;
    }

    const fim = new Date(inicio.value);

    fim.setMinutes(
        fim.getMinutes() + Number(duracao.value)
    );

    fimPrevisto.textContent =
        'Termina em ' +
        fim.toLocaleString(
            'pt-BR',
            {
                dateStyle: 'short',
                timeStyle: 'short'
            }
        );
}


function abrirModalEdicao(id, dataHoraAtual) {
    if (!formEditar || !editDataHora || !modalEditar) {
        return;
    }

    formEditar.action =
        `/agendamentos/${id}/editar`;

    editDataHora.value = dataHoraAtual;

    modalEditar.showModal();
}


function fecharModalEdicao() {
    if (!modalEditar) {
        return;
    }

    modalEditar.close();
}


if (inicio && duracao) {
    inicio.addEventListener(
        'input',
        atualizarFimPrevisto
    );

    duracao.addEventListener(
        'input',
        atualizarFimPrevisto
    );
}

async function copiarTexto(link) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
        try {
            await navigator.clipboard.writeText(link);
            return true;
        } catch (error) {
            // Tenta o fallback legado quando a API é bloqueada ou não está em HTTPS.
        }
    }

    const campoTemporario = document.createElement('textarea');
    campoTemporario.value = link;
    campoTemporario.setAttribute('readonly', '');
    campoTemporario.style.position = 'fixed';
    campoTemporario.style.opacity = '0';
    campoTemporario.style.pointerEvents = 'none';
    document.body.append(campoTemporario);
    campoTemporario.select();
    campoTemporario.setSelectionRange(0, campoTemporario.value.length);

    let copiado = false;
    try {
        copiado = document.execCommand('copy');
    } catch (error) {
        copiado = false;
    }
    campoTemporario.remove();
    return copiado;
}

function mostrarFalhaCopia(area, link) {
    area.replaceChildren();
    area.append(document.createTextNode('Não foi possível copiar automaticamente. Copie o link manualmente:'));

    const campo = document.createElement('input');
    campo.type = 'text';
    campo.readOnly = true;
    campo.value = link;
    campo.setAttribute('aria-label', 'Link de acesso à sessão');
    area.append(campo);
    area.hidden = false;
    campo.focus();
    campo.select();
}

function prepararCopiaLinks() {
    const areaFeedback = document.querySelector('#agenda-feedback');
    if (!areaFeedback) return;

    document.querySelectorAll('[data-copy-session-link]').forEach((botao) => {
        botao.addEventListener('click', async () => {
            const link = botao.dataset.copySessionLink;
            const copiado = await copiarTexto(link);
            if (copiado) {
                areaFeedback.textContent = 'Link copiado!';
                areaFeedback.classList.remove('copy-error');
                areaFeedback.hidden = false;
            } else {
                mostrarFalhaCopia(areaFeedback, link);
                areaFeedback.classList.add('copy-error');
            }
        });
    });

    const linkRecemAgendado = areaFeedback.dataset.copyLinkOnLoad;
    if (linkRecemAgendado) {
        (async () => {
            const copiado = await copiarTexto(linkRecemAgendado);
            if (copiado) {
                areaFeedback.textContent = 'Agendamento concluído. Link copiado!';
                areaFeedback.hidden = false;
            } else {
                mostrarFalhaCopia(areaFeedback, linkRecemAgendado);
                areaFeedback.classList.add('copy-error');
            }
        })();
    }
}

document.addEventListener('DOMContentLoaded', prepararCopiaLinks);

window.abrirModalEdicao = abrirModalEdicao;
window.fecharModalEdicao = fecharModalEdicao;
